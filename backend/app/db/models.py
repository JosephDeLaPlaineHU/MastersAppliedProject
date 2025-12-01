from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum as SQLEnum, JSON, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base

class UserRole(str, enum.Enum):
    STUDENT = "student"
    ASSISTANT = "assistant"
    PROFESSOR = "professor"
    BUSINESS_ADMIN = "business_admin"
    SYS_ADMIN = "sys_admin"

class HypervisorType(str, enum.Enum):
    PROXMOX = "proxmox"
    

# Association Tables
student_courses = Table('student_courses', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)

assistant_courses = Table('assistant_courses', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vms = relationship("VirtualMachine", back_populates="owner")
    
    # Course Relationships
    owned_courses = relationship("Course", back_populates="professor")
    enrolled_courses = relationship("Course", secondary=student_courses, back_populates="students")
    assisting_courses = relationship("Course", secondary=assistant_courses, back_populates="assistants")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    professor_id = Column(Integer, ForeignKey("users.id"))
    template_id = Column(Integer, nullable=True) 
    
    professor = relationship("User", back_populates="owned_courses")
    students = relationship("User", secondary=student_courses, back_populates="enrolled_courses")
    assistants = relationship("User", secondary=assistant_courses, back_populates="assisting_courses")
    vms = relationship("VirtualMachine", back_populates="course")

class Hypervisor(Base):
    __tablename__ = "hypervisors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(SQLEnum(HypervisorType), default=HypervisorType.PROXMOX, nullable=False)
    url = Column(String, nullable=False)
    auth_user = Column(String, nullable=False)
    auth_token = Column(String, nullable=False)
    verify_ssl = Column(Boolean, default=False)

    vms = relationship("VirtualMachine", back_populates="hypervisor")

class VirtualMachine(Base):
    __tablename__ = "virtual_machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    vm_id = Column(Integer)
    status = Column(String, default="stopped")
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    hypervisor_id = Column(Integer, ForeignKey("hypervisors.id"))
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    
    owner = relationship("User", back_populates="vms")
    hypervisor = relationship("Hypervisor", back_populates="vms")
    course = relationship("Course", back_populates="vms")
    
    details = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
