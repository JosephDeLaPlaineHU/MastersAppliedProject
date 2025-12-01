from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.db import models
from pydantic import BaseModel

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserResponse])
def list_users(
    role: Optional[str] = Query(None, description="Filter by user role"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all users.
    Restricted to SYS_ADMIN.
    """
    if current_user.role != models.UserRole.SYS_ADMIN:
        raise HTTPException(status_code=403, detail="Only SysAdmins can list users")

    query = db.query(models.User)
    
    if role:
        query = query.filter(models.User.role == role)
        
    users = query.all()
    return users

class UserDetailResponse(UserResponse):
    vms: List[Any] = []
    courses: List[Any] = []

@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user_details(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get full details for a specific user (VMs, Courses).
    Restricted to SYS_ADMIN.
    """
    if current_user.role != models.UserRole.SYS_ADMIN:
        raise HTTPException(status_code=403, detail="Only SysAdmins can view user details")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prepare Response
    response = UserDetailResponse.model_validate(user)
    
    # VMs
    response.vms = [{"id": vm.id, "name": vm.name, "status": vm.status, "ip": vm.details.get("ip")} for vm in user.vms]
    
    # Courses
    courses = []
    if user.role == models.UserRole.PROFESSOR:
        courses = user.owned_courses
    elif user.role == models.UserRole.STUDENT:
        courses = user.enrolled_courses
    elif user.role == models.UserRole.ASSISTANT:
        courses = user.assisting_courses
        
    response.courses = [{"id": c.id, "name": c.name, "description": c.description} for c in courses]
    
    return response
