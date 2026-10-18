from fastapi import APIRouter
from ..models.canonical import SandboxSpec

router = APIRouter(prefix="/sandboxes", tags=["Developer Testing & Sandboxes"])

@router.post("/provision", response_model=SandboxSpec)
async def provision_sandbox(spec: SandboxSpec):
    """Provisions an isolated microVM sandbox (E2B / Daytona / gVisor) for testing."""
    return spec
