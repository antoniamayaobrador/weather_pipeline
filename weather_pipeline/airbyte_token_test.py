import requests

# Paste your current token here
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vYWlyYnl0ZS1hYmN0bC1haXJieXRlLXdlYmFwcC1zdmM6ODAiLCJhdWQiOiJhaXJieXRlLXNlcnZlciIsInN1YiI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImV4cCI6MTc0NzA3ODY3Niwicm9sZXMiOlsiQVVUSEVOVElDQVRFRF9VU0VSIiwiUkVBREVSIiwiRURJVE9SIiwiQURNSU4iLCJXT1JLU1BBQ0VfUkVBREVSIiwiV09SS1NQQUNFX1JVTk5FUiIsIldPUktTUEFDRV9FRElUT1IiLCJXT1JLU1BBQ0VfQURNSU4iLCJPUkdBTklaQVRJT05fTUVNQkVSIiwiT1JHQU5JWkFUSU9OX1JFQURFUiIsIk9SR0FOSVpBVElPTl9SVU5ORVIiLCJPUkdBTklaQVRJT05fRURJVE9SIiwiT1JHQU5JWkFUSU9OX0FETUlOIl19.bEqsQAcgePiaHM8q1GwGPFOecLg51t6Bx5S2fTre6Nk"
CONNECTION_ID = "e9699c96-c091-4aae-bb59-2943ef432ab7"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

url = "http://localhost:8000/api/v1/connections/sync"
payload = {"connectionId": CONNECTION_ID}

print(f"[DEBUG] Using token (first 20 chars): {AUTH_TOKEN[:20]}...\n")
response = requests.post(url, json=payload, headers=headers)
print(f"Status code: {response.status_code}")
print(f"Response text: {response.text}")
try:
    print("Parsed JSON:", response.json())
except Exception as e:
    print(f"Failed to parse JSON: {e}")
