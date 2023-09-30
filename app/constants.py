origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]
for port in range(5000, 6000):
    origins.append(f"http://localhost:{port}")
