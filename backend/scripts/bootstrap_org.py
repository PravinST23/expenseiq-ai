"""
Bootstrap Org Structure

Author: Pravin Shanmugavel
Project: ExpenseIQ

Sets up the real company reference data after scripts/wipe_data.py:
  - the 8 MAC teams
  - the known client projects under them
  - ONE bootstrap HR_HEAD account (there is no public endpoint to
    create the very first HR_HEAD - same real-world chicken-and-egg
    every company solves by hand once)

*** EDIT THE HR_HEAD SECTION BELOW WITH REAL DETAILS BEFORE RUNNING. ***
Everything else (every other employee, every CFO) should be created
afterwards through the real app - POST /auth/signup for regular
employees, POST /employees/ (as the HR_HEAD you create here) for the
CFO and any other HR_HEAD accounts - never by editing this script or
the database directly.

    python scripts/bootstrap_org.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.models.employee import Employee  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.team import Team  # noqa: E402

# ---------------------------------------------------------
# *** EDIT ME: real HR Head details ***
# ---------------------------------------------------------

HR_HEAD_EMPLOYEE_CODE = "HR001"
HR_HEAD_FULL_NAME = "CHANGE ME"
HR_HEAD_EMAIL = "changeme@example.com"
HR_HEAD_PASSWORD = "ChangeMe@123"  # change on first login

# ---------------------------------------------------------
# Real MAC teams (from the org chart)
# ---------------------------------------------------------

TEAMS = [
    ("MAC1", "Arcturus"),
    ("MAC2", "Hercules"),
    ("MAC3", "Polaris"),
    ("MAC4", "Andromeda"),
    ("MAC5", "Vega"),
    ("MAC6", "Sirius"),
    ("MAC7", "Draco"),
    ("MAC8", "Scorpius"),
]

# ---------------------------------------------------------
# Known client projects (team_code, project_code, project_name)
# ---------------------------------------------------------

PROJECTS = [
    ("MAC3", "GTF", "GTF"),
    ("MAC3", "REVLON", "Revlon"),
    ("MAC3", "STALLION", "Stallion"),
    ("MAC2", "FINVI", "Finvi"),
]


def main():

    db = SessionLocal()

    try:
        teams_by_code = {}

        for team_code, team_name in TEAMS:

            existing = (
                db.query(Team)
                .filter(Team.team_code == team_code)
                .first()
            )

            if existing:
                teams_by_code[team_code] = existing
                continue

            team = Team(team_code=team_code, team_name=team_name)
            db.add(team)
            db.flush()
            teams_by_code[team_code] = team

        db.commit()

        print(f"Teams ready: {len(teams_by_code)}")

        created_projects = 0

        for team_code, project_code, project_name in PROJECTS:

            existing = (
                db.query(Project)
                .filter(Project.project_code == project_code)
                .first()
            )

            if existing:
                continue

            db.add(
                Project(
                    project_code=project_code,
                    project_name=project_name,
                    client_name=project_name,
                    team_id=teams_by_code[team_code].id,
                )
            )
            created_projects += 1

        db.commit()

        print(f"Projects created: {created_projects}")

        existing_hr_head = (
            db.query(Employee)
            .filter(Employee.employee_code == HR_HEAD_EMPLOYEE_CODE)
            .first()
        )

        if existing_hr_head:
            print(
                f"HR Head '{HR_HEAD_EMPLOYEE_CODE}' already exists - "
                "skipping."
            )
        else:
            db.add(
                Employee(
                    employee_code=HR_HEAD_EMPLOYEE_CODE,
                    full_name=HR_HEAD_FULL_NAME,
                    email=HR_HEAD_EMAIL,
                    department="HR",
                    designation="Head of HR",
                    role="HR_HEAD",
                    hashed_password=hash_password(HR_HEAD_PASSWORD),
                )
            )
            db.commit()
            print(
                f"HR Head created: {HR_HEAD_EMAIL} "
                f"(password: {HR_HEAD_PASSWORD} - change it on first "
                "login)."
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()
