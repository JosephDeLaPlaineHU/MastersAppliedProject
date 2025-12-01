import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.db.base import SessionLocal
from app.db import models

def print_course_report():
    db = SessionLocal()
    try:
        courses = db.query(models.Course).all()
        print(f"\n{'='*60}")
        print(f"{'COURSE REPORT':^60}")
        print(f"{'='*60}\n")

        for course in courses:
            print(f"Course: {course.name} (ID: {course.id})")
            print(f"Description: {course.description}")
            print(f"Template ID: {course.template_id}")
            print("-" * 40)

            # 1. Professor
            prof = course.professor
            print(f"  [Professor]")
            if prof:
                print(f"    - {prof.username} ({prof.email})")
                prof_vms = db.query(models.VirtualMachine).filter(
                    models.VirtualMachine.owner_id == prof.id,
                    models.VirtualMachine.course_id == course.id
                ).all()
                if prof_vms:
                    for vm in prof_vms:
                        print(f"      * VM: {vm.name} (ID: {vm.vm_id}, Status: {vm.status})")
                else:
                    print(f"      * No VMs")
            else:
                print("    - None")

            # 2. Assistants
            if course.assistants:
                print(f"\n  [Assistants]")
                for assistant in course.assistants:
                    print(f"    - {assistant.username} ({assistant.email})")
                    asst_vms = db.query(models.VirtualMachine).filter(
                        models.VirtualMachine.owner_id == assistant.id,
                        models.VirtualMachine.course_id == course.id
                    ).all()
                    if asst_vms:
                        for vm in asst_vms:
                            print(f"      * VM: {vm.name} (ID: {vm.vm_id}, Status: {vm.status})")
                    else:
                        print(f"      * No VMs")
            
            # 3. Students
            if course.students:
                print(f"\n  [Students]")
                for student in course.students:
                    print(f"    - {student.username} ({student.email})")
                    student_vms = db.query(models.VirtualMachine).filter(
                        models.VirtualMachine.owner_id == student.id,
                        models.VirtualMachine.course_id == course.id
                    ).all()
                    if student_vms:
                        for vm in student_vms:
                            print(f"      * VM: {vm.name} (ID: {vm.vm_id}, Status: {vm.status})")
                    else:
                        print(f"      * No VMs")
            
            print("\n" + "="*60 + "\n")

    finally:
        db.close()

if __name__ == "__main__":
    print_course_report()
