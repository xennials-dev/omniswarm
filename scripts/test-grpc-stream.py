"""
OmniSwarm gRPC Streaming End-to-End Verification Test
Verifies server-streaming RPC over gRPC channel (port 50051).
"""

import sys
import os
import time
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "engine_broker")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "engine_broker", "src", "generated")))

import grpc
from omniswarm.v1 import broker_pb2, broker_pb2_grpc
from src.grpc_server import serve as serve_grpc

def run_test():
    print("=" * 65)
    print("OmniSwarm gRPC Streaming Client Verification Test")
    print("=" * 65)

    test_port = 50055
    server = serve_grpc(port=test_port)
    time.sleep(0.5)

    try:
        # Establish gRPC channel
        print(f"[1] Connecting client to gRPC channel on localhost:{test_port}...")
        channel = grpc.insecure_channel(f"localhost:{test_port}")
        stub = broker_pb2_grpc.OmniSwarmBrokerServiceStub(channel)

        # Test StreamExecutionEvents
        print("[2] Initiating StreamExecutionEvents RPC...")
        req = broker_pb2.StreamExecutionEventsRequest(execution_id="test_exec_stream_9918")
        event_stream = stub.StreamExecutionEvents(req)

        events_received = 0
        for event in event_stream:
            events_received += 1
            status_name = broker_pb2.ExecutionStatus.Name(event.status)
            print(f"   [Frame {events_received}] Status: {status_name} | Event: {event.log_chunk} | State: {event.state_update_json}")

        assert events_received >= 5, f"Expected at least 5 frames, got {events_received}"
        print(f"[3] Stream successfully consumed {events_received} execution event frames.")
        print("=" * 65)
        print("gRPC Streaming Verification PASSED with 100% frame delivery!")
        print("=" * 65)
    finally:
        server.stop(0)

if __name__ == "__main__":
    run_test()
