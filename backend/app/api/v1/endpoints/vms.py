from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.db import models
from app.hypervisor.manager import HypervisorManager
from pydantic import BaseModel

router = APIRouter()

class VMCreate(BaseModel):
    name: str
    template_id: int
    course_id: int
    cpu: int = 2
    memory: int = 2048

class VMResponse(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    vm_id: Optional[int] = None
    status: Optional[str] = None
    ip_address: Optional[str] = None
    owner_email: Optional[str] = None
    course_name: Optional[str] = None
    details: Any = {}
    
    class Config:
        from_attributes = True

@router.get("/templates", response_model=List[Any])
def list_templates(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List available VM templates from Proxmox.
    """
    client = HypervisorManager.get_client()
    return client.list_templates()

@router.get("/", response_model=None)
def list_vms(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List VMs based on Role:
    - SYS_ADMIN: All VMs
    - BUSINESS_ADMIN: All VMs (Read-only)
    - PROFESSOR: VMs in owned courses
    - ASSISTANT: VMs in assisted courses
    - STUDENT: Only own VMs
    """

    try:
        with open("c:/Users/badda/Desktop/MastersProject/backend/startup.log", "a") as f:
            f.write("ENDPOINT: ENTERED list_vms\n")
    except:
        pass
    try:
        if current_user.role in [models.UserRole.SYS_ADMIN, models.UserRole.BUSINESS_ADMIN]:
            vms = db.query(models.VirtualMachine).all()
        elif current_user.role == models.UserRole.PROFESSOR:
            vms = db.query(models.VirtualMachine).join(models.Course).filter(models.Course.professor_id == current_user.id).all()
        elif current_user.role == models.UserRole.ASSISTANT:
            course_ids = [c.id for c in current_user.assisting_courses]
            vms = db.query(models.VirtualMachine).filter(models.VirtualMachine.course_id.in_(course_ids)).all()
        else:
            vms = db.query(models.VirtualMachine).filter(models.VirtualMachine.owner_id == current_user.id).all()

        client = HypervisorManager.get_client()
        results = []
        for vm in vms:
            try:
                vm_data = VMResponse.model_validate(vm)
                if vm.owner:
                    vm_data.owner_email = vm.owner.email
                if vm.course:
                    vm_data.course_name = vm.course.name
            except Exception as e:
                with open("c:/Users/badda/Desktop/MastersProject/backend/validation_error.log", "w") as f:
                    f.write(f"Validation Error for VM {vm.id}: {str(e)}\n")
                    f.write(str(vm.__dict__))
                raise e

            if vm.status == "running":
                try:
                    details = client.get_vm_details(vm.vm_id)
                    vm_data.ip_address = details.get("ip")
                except:
                    pass
            results.append(vm_data)
            
        return results
    except Exception as e:
        import traceback
        with open("c:/Users/badda/Desktop/MastersProject/backend/error.log", "w") as f:
            f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"List VMs Failed: {str(e)}")

@router.post("/", response_model=Any)
def create_vm(
    vm_in: VMCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new VM from a template.
    Restricted to PROFESSOR and SYS_ADMIN.
    """
    if current_user.role not in [models.UserRole.PROFESSOR, models.UserRole.SYS_ADMIN]:
        raise HTTPException(status_code=403, detail="Students and Assistants cannot create VMs")

    course = db.query(models.Course).filter(models.Course.id == vm_in.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if current_user.role == models.UserRole.PROFESSOR and course.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only create VMs for your own courses")

    client = HypervisorManager.get_client()
    
    try:
        result = client.create_vm(vm_in.name, {
            "template_id": vm_in.template_id,
            "cpu": vm_in.cpu,
            "memory": vm_in.memory
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    vm = models.VirtualMachine(
        name=vm_in.name,
        owner_id=current_user.id,
        vm_id=result.get("vmid"),
        course_id=vm_in.course_id,
        status="creating",
        details={"node": result.get("node")}
    )
    db.add(vm)
    db.commit()
    
    return result

@router.post("/{vm_id}/start", response_model=Any)
def start_vm(
    vm_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if current_user.role == models.UserRole.BUSINESS_ADMIN:
        raise HTTPException(status_code=403, detail="Business Admins cannot perform actions")
        
    vm = db.query(models.VirtualMachine).filter(models.VirtualMachine.vm_id == int(vm_id)).first()
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
        
    if current_user.role == models.UserRole.STUDENT and vm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to start this VM")
        
    client = HypervisorManager.get_client()
    success = client.start_vm(vm_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to start VM")
    return {"message": "VM started"}

@router.post("/{vm_id}/stop", response_model=Any)
def stop_vm(
    vm_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if current_user.role == models.UserRole.BUSINESS_ADMIN:
        raise HTTPException(status_code=403, detail="Business Admins cannot perform actions")

    vm = db.query(models.VirtualMachine).filter(models.VirtualMachine.vm_id == int(vm_id)).first()
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
        
    if current_user.role == models.UserRole.STUDENT and vm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to stop this VM")

    client = HypervisorManager.get_client()
    success = client.stop_vm(vm_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop VM")
    return {"message": "VM stopped"}

@router.post("/{vm_id}/shutdown", response_model=Any)
def shutdown_vm(
    vm_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if current_user.role == models.UserRole.BUSINESS_ADMIN:
        raise HTTPException(status_code=403, detail="Business Admins cannot perform actions")

    vm = db.query(models.VirtualMachine).filter(models.VirtualMachine.vm_id == int(vm_id)).first()
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
        
    if current_user.role == models.UserRole.STUDENT and vm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to shutdown this VM")

    client = HypervisorManager.get_client()
    success = client.shutdown_vm(vm_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to shutdown VM")
    return {"message": "VM shutdown initiated"}

@router.get("/{vm_id}/stats", response_model=Any)
def get_vm_stats(
    vm_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get real-time stats and cost estimation for a VM.
    """
    client = HypervisorManager.get_client()
    stats = client.get_vm_stats(vm_id)
    
    if stats.get("status") == "error":
        raise HTTPException(status_code=404, detail=stats.get("details"))
        
    # Temporary cost calculation model that will need to be replaced with the actual model in the future
    details = client.get_vm_details(vm_id)
    config = details.get("config", {})
    
    cores = int(config.get("cores", 1))
    memory_mb = int(config.get("memory", 1024))
    memory_gb = memory_mb / 1024
    
    monthly_cost = (cores * 5.0) + (memory_gb * 2.0)
    
    stats["cost_estimate"] = {
        "monthly_usd": round(monthly_cost, 2),
        "breakdown": f"${cores*5} (CPU) + ${round(memory_gb*2, 2)} (RAM)"
    }
    
    return stats

@router.post("/{vm_id}/console", response_model=Any)
def get_vm_console(
    vm_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get NoVNC console ticket for a VM.
    """
    vm = db.query(models.VirtualMachine).filter(models.VirtualMachine.id == vm_id).first()
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")

    if current_user.role not in [models.UserRole.SYS_ADMIN, models.UserRole.BUSINESS_ADMIN]:
        if vm.owner_id != current_user.id:
            course = vm.course
            if current_user.role == models.UserRole.PROFESSOR and course.professor_id == current_user.id:
                pass
            elif current_user.role == models.UserRole.ASSISTANT and current_user in course.assistants:
                pass
            else:
                raise HTTPException(status_code=403, detail="Not enough permissions")

    client = HypervisorManager.get_client()
    try:
        ticket_data = client.get_console_ticket(vm.vm_id)
        host = ticket_data['host']
        if ":" not in host:
             host = f"{host}:8006"
             
        direct_url = f"https://{host}/?console=kvm&novnc=1&vmid={vm.vm_id}&node={ticket_data['node']}"
        
        return {
            "ticket": ticket_data,
            "direct_url": direct_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TemplateBuildRequest(BaseModel):
    name: str
    iso_file: str
    cpu: int = 2
    memory: int = 2048
    disk_size: str = "32G"

@router.post("/templates/build", response_model=Any)
def build_template_vm(
    build_in: TemplateBuildRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a 'Draft VM' from an ISO to be used for creating a template.
    SysAdmin Only.
    """
    if current_user.role != models.UserRole.SYS_ADMIN:
        raise HTTPException(status_code=403, detail="Only SysAdmins can build templates")

    client = HypervisorManager.get_client()
    try:
        result = client.create_vm_from_iso(
            name=build_in.name,
            iso_file=build_in.iso_file,
            config={
                "cpu": build_in.cpu,
                "memory": build_in.memory,
                "disk_size": build_in.disk_size
            }
        )
        
        vm = models.VirtualMachine(
            name=build_in.name,
            owner_id=current_user.id,
            vm_id=result.get("vmid"),
            course_id=None, 
            status="draft_template",
            details={"node": result.get("node"), "iso": build_in.iso_file}
        )
        db.add(vm)
        db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/templates/{vm_id}/finalize", response_model=Any)
def finalize_template(
    vm_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Convert a Draft VM into a Template.
    SysAdmin Only.
    """
    if current_user.role != models.UserRole.SYS_ADMIN:
        raise HTTPException(status_code=403, detail="Only SysAdmins can finalize templates")

    vm = db.query(models.VirtualMachine).filter(models.VirtualMachine.id == vm_id).first()
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")

    client = HypervisorManager.get_client()
    try:
        success = client.convert_to_template(vm.vm_id)
        if success:
            vm.status = "template"
            db.commit()
            return {"message": "VM converted to template successfully"}
        else:
            raise Exception("Hypervisor failed to convert")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class VMAssignRequest(BaseModel):
    email: str
    course_id: Optional[int] = None

@router.post("/{vm_id}/assign", response_model=Any)
def assign_vm(
    vm_id: int,
    assign_in: VMAssignRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Assign an existing VM to a student and optionally to a course.
    Accessible by:
    - SYS_ADMIN: Can assign ANY VM to ANY Course.
    - PROFESSOR: Can assign VMs belonging to their courses, OR assign a VM to one of their courses.
    """
    vm = db.query(models.VirtualMachine).filter(models.VirtualMachine.id == vm_id).first()
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")

    if current_user.role == models.UserRole.SYS_ADMIN:
        pass 
    elif current_user.role == models.UserRole.PROFESSOR:
        if vm.course and vm.course.professor_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not authorized to reassign this VM")
        if not vm.course and vm.owner_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not authorized to reassign this VM")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    target_user = db.query(models.User).filter(models.User.email == assign_in.email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    if assign_in.course_id:
        course = db.query(models.Course).filter(models.Course.id == assign_in.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Target course not found")
            
        if current_user.role == models.UserRole.PROFESSOR and course.professor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot assign VM to a course you do not own")
            
        vm.course_id = course.id

    vm.owner_id = target_user.id
    db.commit()

    msg = f"VM {vm.name} assigned to {target_user.username}"
    if assign_in.course_id:
        msg += f" in course {vm.course.name}"
        
    return {"message": msg}
