import urllib.request, json
base = "http://localhost:8888/api/v1"
try:
    d = json.dumps({"username":"test","email":"test@test.com","password":"test123456"}).encode()
    r = urllib.request.urlopen(base + "/auth/register", d, timeout=10)
    print("Register:", r.status, json.loads(r.read()))
except Exception as e:
    print("Register:", e)
