"""Automated API contract verification script.

Verifies that FastAPI routes match frontend client expectations in frontend/src/lib/api.ts
to prevent endpoint drift and schema divergence.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from src.api.main import app

REQUIRED_CONTRACTS = [
    {
        "endpoint": "/api/diagnosis/analyze",
        "method": "POST",
        "description": "Symptom diagnosis endpoint",
        "sample_body": {"text": "Fever, cough, and fatigue"},
        "expected_response_fields": ["diagnosis", "severity", "recommendations", "disclaimer"],
    },
    {
        "endpoint": "/api/vision/analyze",
        "method": "POST",
        "description": "Medical image analysis endpoint",
        "verify_route_exists": True,
    },
    {
        "endpoint": "/api/chat/message",
        "method": "POST",
        "description": "Conversational assistant endpoint",
        "sample_body": {"message": "What is hypertension?"},
        "expected_response_fields": ["conversation_id", "response", "timestamp"],
    },
    {
        "endpoint": "/api/history",
        "method": "GET",
        "description": "Diagnostic session history endpoint",
        "expected_response_fields": ["sessions", "total"],
    },
    {
        "endpoint": "/health",
        "method": "GET",
        "description": "System health and agent status endpoint",
        "expected_response_fields": ["status", "agents", "models"],
    },
]


def verify_contracts() -> bool:
    client = TestClient(app)
    all_passed = True

    print("=" * 60)
    print("Multi-Agent AI Diagnostic System — API Contract Verifier")
    print("=" * 60)

    for contract in REQUIRED_CONTRACTS:
        endpoint = contract["endpoint"]
        method = contract["method"]
        desc = contract["description"]

        print(f"\n[Verifying] {method} {endpoint} ({desc})")

        if contract.get("verify_route_exists"):
            # Check route in openapi schema
            openapi = app.openapi()
            paths = openapi.get("paths", {})
            if endpoint in paths and method.lower() in paths[endpoint]:
                print(f"  ✓ Route registered in OpenAPI spec: {endpoint}")
            else:
                print(f"  ✗ Route NOT found in OpenAPI schema: {endpoint}")
                all_passed = False
            continue

        if method == "GET":
            response = client.get(endpoint)
        elif method == "POST":
            response = client.post(endpoint, json=contract.get("sample_body", {}))
        else:
            response = None

        if response is None:
            print(f"  ✗ Unsupported HTTP method: {method}")
            all_passed = False
            continue

        if response.status_code != 200:
            print(f"  ✗ Request failed with status {response.status_code}: {response.text[:120]}")
            all_passed = False
            continue

        data = response.json()
        missing_fields = []
        for field in contract.get("expected_response_fields", []):
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            print(f"  ✗ Missing expected response fields: {', '.join(missing_fields)}")
            all_passed = False
        else:
            print(f"  ✓ Contract verified: HTTP 200 with all expected fields")

    print("\n" + "=" * 60)
    if all_passed:
        print("RESULT: All API contracts verified successfully! No schema drift.")
        print("=" * 60)
        return True
    else:
        print("RESULT: One or more API contract verifications failed.")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = verify_contracts()
    sys.exit(0 if success else 1)
