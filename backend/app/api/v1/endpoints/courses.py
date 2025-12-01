from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api import deps
from app.db import models
from app.hypervisor.manager import HypervisorManager
from pydantic import BaseModel

router = APIRouter()

class CourseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template_id: Optional[int] = None

class CourseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    professor_id: int
    template_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class EnrollRequest(BaseModel):
    email: str

class ProvisionRequest(BaseModel):
    student_email: Optional[str] = None 

@router.post("/", response_model=CourseResponse)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new course.
    Only Professors and Sys Admins can create courses.
    """
    if current_user.role not in [models.UserRole.PROFESSOR, models.UserRole.SYS_ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    course = models.Course(
        name=course_in.name,
        description=course_in.description,
        professor_id=current_user.id,
        template_id=course_in.template_id
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

    return course

class CourseDetailResponse(CourseResponse):
    professor: Optional[Any] = None
    students: List[Any] = []
    assistants: List[Any] = []

@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course_details(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get full course details (Professor, Students, Assistants).
    Accessible by: SysAdmin, Course Professor, Course Assistants.
    """
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    
    is_sys_admin = current_user.role == models.UserRole.SYS_ADMIN
    is_professor = current_user.id == course.professor_id
    is_assistant = current_user in course.assistants
    
    if not (is_sys_admin or is_professor or is_assistant):
        raise HTTPException(status_code=403, detail="Not authorized to view this course")

    response = CourseDetailResponse.model_validate(course)
    
    
    if course.professor:
        response.professor = {"username": course.professor.username, "email": course.professor.email}
        
    response.students = [{"username": s.username, "email": s.email} for s in course.students]
    response.assistants = [{"username": a.username, "email": a.email} for a in course.assistants]
    
    return response

@router.get("/", response_model=List[CourseResponse])
def list_courses(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List courses.
    - Students: Only enrolled courses.
    - Assistants: Only assisting courses.
    - Professors: Only owned courses.
    - Sys Admin: All courses.
    """
    if current_user.role == models.UserRole.SYS_ADMIN:
        return db.query(models.Course).all()
    elif current_user.role == models.UserRole.PROFESSOR:
        return db.query(models.Course).filter(models.Course.professor_id == current_user.id).all()
    elif current_user.role == models.UserRole.ASSISTANT:
        return current_user.assisting_courses
    elif current_user.role == models.UserRole.STUDENT:
        return current_user.enrolled_courses
    else:
        return []

@router.post("/{course_id}/enroll", response_model=Any)
def enroll_student(
    course_id: int,
    enroll_in: EnrollRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Enroll a student in a course and auto-provision VM.
    """
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if current_user.role != models.UserRole.SYS_ADMIN and course.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    student = db.query(models.User).filter(models.User.email == enroll_in.email).first()
    if not student:
        raise HTTPException(status_code=404, detail="User not found")
        
    if student.role == models.UserRole.STUDENT:
        if student not in course.students:
            course.students.append(student)
            if course.template_id:
                background_tasks.add_task(provision_vm_for_student, db, course, student)
                
    elif student.role == models.UserRole.ASSISTANT:
        if student not in course.assistants:
            course.assistants.append(student)
    else:
        raise HTTPException(status_code=400, detail="Can only enroll Students or Assistants")
        
    db.commit()
    return {"message": f"User {student.email} enrolled in course {course.name}. VM provisioning started."}

def provision_vm_for_student(db: Session, course: models.Course, student: models.User):
    """
    Helper function to provision a VM for a single student in a course.
    """
    
    existing_vm = db.query(models.VirtualMachine).filter(
        models.VirtualMachine.owner_id == student.id,
        models.VirtualMachine.course_id == course.id
    ).first()
    
    if existing_vm:
        return 
        
    client = HypervisorManager.get_client()
    
    
    vm_name = f"{course.name.replace(' ', '-')}-{student.username}"
    vm_name = "".join(c for c in vm_name if c.isalnum() or c in "-").lower()
    
    try:
        
        result = client.create_vm(vm_name, {
            "template_id": course.template_id,
            "cpu": 2, 
            "memory": 1024
        })
        
        
        new_vm = models.VirtualMachine(
            name=vm_name,
            owner_id=student.id,
            vm_id=result.get("vmid"),
            course_id=course.id,
            status="creating",
            details={"node": result.get("node")}
        )
        db.add(new_vm)
        db.commit()
        print(f"Successfully provisioned VM {vm_name} for {student.username}")
        
    except Exception as e:
        print(f"Failed to provision for {student.username}: {e}")

@router.post("/{course_id}/provision", response_model=Any)
def provision_vms(
    course_id: int,
    provision_in: ProvisionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Provision VMs for students in the course based on the Course Template.
    Only Professor/SysAdmin.
    """

    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if current_user.role != models.UserRole.SYS_ADMIN and course.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    if not course.template_id:
        raise HTTPException(status_code=400, detail="Course has no template assigned")

    targets = []
    if provision_in.student_email:
        student = db.query(models.User).filter(models.User.email == provision_in.student_email).first()
        if not student or student not in course.students:
            raise HTTPException(status_code=400, detail="Student not found or not enrolled")
        targets.append(student)
    else:
        targets = course.students

    for student in targets:
        background_tasks.add_task(provision_vm_for_student, db, course, student)
    
    return {"message": f"Provisioning triggered for {len(targets)} students."}

@router.get("/{course_id}/students", response_model=Any)
def list_course_students(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all students in a course and their associated VMs.
    Accessible by: SysAdmin, Course Professor, Course Assistants.
    """
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    
    is_sys_admin = current_user.role == models.UserRole.SYS_ADMIN
    is_professor = current_user.id == course.professor_id
    is_assistant = current_user in course.assistants
    
    if not (is_sys_admin or is_professor or is_assistant):
        raise HTTPException(status_code=403, detail="Not authorized to view this course's students")

    results = []
    for student in course.students:
        vm = db.query(models.VirtualMachine).filter(
            models.VirtualMachine.owner_id == student.id,
            models.VirtualMachine.course_id == course.id
        ).first()
        
        student_data = {
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "vm": {
                "id": vm.id,
                "name": vm.name,
                "status": vm.status,
                "ip": vm.details.get("ip") if vm.details else None
            } if vm else None
        }
        results.append(student_data)
        
    return results

@router.get("/{course_id}/assistants", response_model=Any)
def list_course_assistants(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all assistants in a course.
    Accessible by: SysAdmin, Course Professor.
    """
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    is_sys_admin = current_user.role == models.UserRole.SYS_ADMIN
    is_professor = current_user.id == course.professor_id
    
    if not (is_sys_admin or is_professor):
        raise HTTPException(status_code=403, detail="Not authorized to view this course's assistants")

    results = []
    for assistant in course.assistants:
        results.append({
            "id": assistant.id,
            "username": assistant.username,
            "email": assistant.email
        })
        
    return results

class AssignProfessorRequest(BaseModel):
    email: str

@router.put("/{course_id}/professor", response_model=Any)
def assign_professor(
    course_id: int,
    assign_in: AssignProfessorRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Assign a professor to a course.
    SYS_ADMIN only.
    """
    if current_user.role != models.UserRole.SYS_ADMIN:
        raise HTTPException(status_code=403, detail="Only SysAdmins can assign professors")

    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    professor = db.query(models.User).filter(models.User.email == assign_in.email).first()
    if not professor:
        raise HTTPException(status_code=404, detail="Professor user not found")
        
    if professor.role != models.UserRole.PROFESSOR:
        raise HTTPException(status_code=400, detail="User is not a professor")

    course.professor_id = professor.id
    db.commit()
    
    return {"message": f"Professor {professor.username} assigned to course {course.name}"}
