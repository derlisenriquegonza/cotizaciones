import json
from server import app

client = app.test_client()

print("==========================================")
print("TESTING SERVER ENDPOINTS (Werkzeug Test Client)")
print("==========================================")

# 1. Test Static Files
static_endpoints = ["/", "/styles.css", "/app.js", "/manifest.json", "/sw.js", "/icon.svg"]
for path in static_endpoints:
    res = client.get(path)
    print(f"GET {path} -> Status {res.status_code}, Length {len(res.data)} bytes")
    assert res.status_code == 200, f"Failed static endpoint {path}"

# 2. Test Live API Endpoint
print("\n--- Testing GET /api/rates ---")
res = client.get("/api/rates")
print(f"GET /api/rates -> Status {res.status_code}")
assert res.status_code == 200

rates = json.loads(res.data.decode('utf-8'))
print(f"Total Houses returned: {len(rates)}\n")

for item in rates:
    print(f"HOUSE: {item.get('source')} ({item.get('branch')})")
    print(f"   Status: {item.get('status')}")
    print(f"   USD/PYG: Buy {item.get('usd_pyg', {}).get('buy')} | Sell {item.get('usd_pyg', {}).get('sell')}")
    print(f"   BRL/PYG: Buy {item.get('brl_pyg', {}).get('buy')} | Sell {item.get('brl_pyg', {}).get('sell')}")
    print(f"   USD/BRL: Buy {item.get('usd_brl', {}).get('buy')} | Sell {item.get('usd_brl', {}).get('sell')}")
    print(f"   Fuente actualizada: {item.get('sourceUpdatedAt')}")
    print(f"   Consultado: {item.get('retrievedAt')}\n")

print("==========================================")
print("ALL E2E SERVER TESTS PASSED SUCCESSFULLY!")
print("==========================================")
