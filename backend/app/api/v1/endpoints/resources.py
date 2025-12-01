from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api import deps
from app.db import models
from app.hypervisor.manager import HypervisorManager

router = APIRouter()

@router.get("/isos", response_model=List[Any])
def list_isos(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List available ISO images in Proxmox storage.
    Accessible by SYS_ADMIN and PROFESSOR (to know what they can request).
    """
    if current_user.role not in [models.UserRole.SYS_ADMIN, models.UserRole.PROFESSOR]:
        raise HTTPException(status_code=403, detail="Not authorized to view ISOs")

    client = HypervisorManager.get_client()
    return client.list_isos()

class ISODownloadRequest(BaseModel):
    url: str
    file_name: str
    storage: str = "local"

@router.post("/isos/download", response_model=Any)
def download_iso(
    download_in: ISODownloadRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Trigger Proxmox to download an ISO from a URL.
    Returns the Task UPID.
    SysAdmin Only.
    """
    if current_user.role != models.UserRole.SYS_ADMIN:
        raise HTTPException(status_code=403, detail="Only SysAdmins can download ISOs")

    client = HypervisorManager.get_client()
    try:
        upid = client.download_iso(download_in.url, download_in.file_name, download_in.storage)
        return {"upid": upid, "message": "Download started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/{upid}", response_model=Any)
def get_task_status(
    upid: str,
    node: str = "pve",
    # UPID format: UPID:node:hex:hex:hex:user:id:
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get status of a background task.
    """
    if current_user.role != models.UserRole.SYS_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        # UPID:node:pid:pstart:starttime:type:id:user@realm:
        parts = upid.split(":")
        if len(parts) > 1:
            node = parts[1]
    except:
        pass

    client = HypervisorManager.get_client()
    status = client.get_task_status(upid, node)
    logs = client.get_task_log(upid, node)
    

    progress = 0
    for line in logs:
        if "progress" in line.lower() or "%" in line:
            # Try to extract number
            import re
            match = re.search(r'(\d+)%', line)
            if match:
                progress = int(match.group(1))
    
    return {
        "status": status,
        "progress": progress,
        "logs": logs[-5:] # Last 5 lines
    }

@router.delete("/tasks/{upid}", response_model=Any)
def cancel_task(
    upid: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Cancel a running task.
    """
    if current_user.role != models.UserRole.SYS_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    node = "pve"
    try:
        parts = upid.split(":")
        if len(parts) > 1:
            node = parts[1]
    except:
        pass

    client = HypervisorManager.get_client()
    success = client.cancel_task(upid, node)
    if success:
        return {"message": "Task cancellation requested"}
    else:
        raise HTTPException(status_code=400, detail="Failed to cancel task")
