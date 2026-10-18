"""
OmniSwarm Engine Broker Dual-Stack Server Runner
Runs FastAPI (REST/HTTP :8000) and gRPC Server (:50051) concurrently.
"""

import sys
import os
import threading
import uvicorn

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "generated")))

from src.main import app
from src.grpc_server import serve as serve_grpc

def start_grpc():
    grpc_server = serve_grpc(port=50051)
    grpc_server.wait_for_termination()

def main():
    print("=" * 60)
    print("Starting OmniSwarm Engine Broker Dual-Stack Control Plane")
    print("=" * 60)

    # Launch gRPC Server in background daemon thread
    grpc_thread = threading.Thread(target=start_grpc, daemon=True)
    grpc_thread.start()

    # Launch FastAPI Server in main thread
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()
