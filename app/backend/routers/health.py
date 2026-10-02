from fastapi import APIRouter, HTTPException, Request
from agents.definitions import TEAM

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health(request: Request):
    client = request.app.state.foundry_client
    identities = client.identities() if hasattr(client, "identities") else [
        {"id": role, "name": item["name"], "version": None, "registered": False}
        for role, item in TEAM.items()
    ]
    return {"status": "ok", "configured": client is not None, "agents": identities}


@router.get("/api/deployments")
async def deployments(request: Request):
    """Read-only setup diagnostics; the backend alone reads configuration."""
    client = request.app.state.foundry_client
    if not hasattr(client, "project"):
        raise HTTPException(503, "Configure the backend first.")
    names = [deployment.name async for deployment in client.project.deployments.list()]
    return {"available_deployments": names,
            "configured_deployment_exists": client.settings.azure_ai_model_deployment_name in names}
