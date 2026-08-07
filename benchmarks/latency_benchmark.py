import asyncio
import time
import json
import os
import httpx
import numpy as np
from pathlib import Path

# Create a sample text file to benchmark if we don't have one
SAMPLE_FILE_PATH = "benchmarks/sample_text.txt"
if not os.path.exists("benchmarks"):
    os.makedirs("benchmarks")
if not os.path.exists(SAMPLE_FILE_PATH):
    with open(SAMPLE_FILE_PATH, "w") as f:
        f.write("This is a sample document for John Doe. Email: john.doe@example.com. Phone: 555-123-4567. " * 100)

BASE_URL = "http://localhost:8001"
# For dev bypass
HEADERS = {}

async def measure_request(client, endpoint, method="GET", files=None, data=None):
    start = time.time()
    if method == "GET":
        resp = await client.get(f"{BASE_URL}{endpoint}", headers=HEADERS)
    else:
        resp = await client.post(f"{BASE_URL}{endpoint}", headers=HEADERS, files=files, data=data)
    
    latency = (time.time() - start) * 1000  # ms
    return latency, resp.status_code

async def run_benchmark(num_requests=20, output_file="benchmarks/before.json"):
    print(f"Starting latency benchmark with {num_requests} requests...")
    
    latencies = []
    errors = 0
    
    # We use httpx AsyncClient for async requests
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(num_requests):
            with open(SAMPLE_FILE_PATH, "rb") as f:
                files = {"file": ("sample_text.txt", f, "text/plain")}
                try:
                    lat, status = await measure_request(client, "/process", method="POST", files=files)
                    if status in (200, 202):
                        latencies.append(lat)
                    else:
                        errors += 1
                except Exception as e:
                    errors += 1
                    print(f"Error: {e}")
                    
            print(f"Request {i+1}/{num_requests} complete.")
            await asyncio.sleep(0.1) # slight delay to avoid overwhelming simple server
            
    if not latencies:
        print("No successful requests. Ensure server is running on localhost:8001")
        return
        
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)
    avg = np.mean(latencies)
    
    results = {
        "num_requests": num_requests,
        "successful": len(latencies),
        "errors": errors,
        "latencies_ms": {
            "p50": round(p50, 2),
            "p95": round(p95, 2),
            "p99": round(p99, 2),
            "avg": round(avg, 2),
            "min": round(min(latencies), 2),
            "max": round(max(latencies), 2)
        }
    }
    
    print("\nBenchmark Results:")
    print(json.dumps(results, indent=2))
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\nSaved results to {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="benchmarks/before.json", help="Output file")
    parser.add_argument("--n", type=int, default=20, help="Number of requests")
    args = parser.parse_args()
    
    asyncio.run(run_benchmark(num_requests=args.n, output_file=args.out))
