"""
Project: AlphaQuant AI
File: backend/api/v1/auth.py
Description: Authentication and user registration API routes.
Python Version: 3.11.9
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.responses import APIResponse, build_success_response
from backend.core.exceptions import AuthenticationException, BusinessException
from backend.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from backend.database.session import get_session
from backend.models.user import User
from backend.schemas.auth import UserCreateRequest, UserLoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=APIResponse[UserResponse])
async def register(
    request: UserCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> APIResponse[UserResponse]:
    existing = await session.execute(
        select(User).where(
            (User.username == request.username) | (User.email == request.email)
        )
    )
    if existing.scalar_one_or_none():
        raise BusinessException("用户名或邮箱已存在")
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return build_success_response(UserResponse.model_validate(user))


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    request: UserLoginRequest,
    session: AsyncSession = Depends(get_session),
) -> APIResponse[TokenResponse]:
    stmt = select(User).where(
        (User.username == request.username_or_email)
        | (User.email == request.username_or_email)
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not verify_password(request.password, user.hashed_password):
        raise AuthenticationException("用户名/邮箱或密码错误")
    if not user.is_active:
        raise AuthenticationException("账户已被禁用")
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return build_success_response(
        TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=60,
        )
    )
