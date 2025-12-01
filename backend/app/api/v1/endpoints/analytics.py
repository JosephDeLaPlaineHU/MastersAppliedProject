from typing import Any
from fastapi import APIRouter, Depends
from app.api import deps
from app.db import models
from app.hypervisor.manager import HypervisorManager

router = APIRouter()

@router.get("/", response_model=Any)
def get_system_analytics(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get system-wide analytics.
    """
    client = HypervisorManager.get_client()
    return client.get_analytics()
