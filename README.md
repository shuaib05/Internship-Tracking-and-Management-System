# College Internship Tracking and Management System (ITMS)

A web-based application to streamline and manage internship activities within a college. Built with Flask and MySQL.

## Features

- **Student Portal** — Browse internships, apply, track application status, manage profile
- **Admin Portal** — Manage companies, internships, students, and update application statuses
- **Faculty Portal** — Monitor assigned internships and student applications
- **Reports** — View analytics on applications by department, company, acceptance rate, and top internships
- **Role-based Authentication** — Secure login with separate dashboards for each role

## Tech Stack

- **Frontend:** HTML, CSS, Jinja2 templating
- **Backend:** Python (Flask)
- **Database:** MySQL

## Project Structure

```
College Internship Tracking and Management System/
├── backend/
│   └── app.py
├── frontend/
│   ├── base.html
│   ├── login.html
│   ├── student_dashboard.html
│   ├── student_profile.html
│   ├── student_internships.html
│   ├── student_applications.html
│   ├── admin_dashboard.html
│   ├── admin_companies.html
│   ├── admin_internships.html
│   ├── admin_students.html
│   ├── admin_applications.html
│   ├── faculty_dashboard.html
│   ├── faculty_applications.html
│   ├── faculty_internships.html
│   └── reports.html
├── schema.sql
├── requirements.txt
└── README.md
```

## Database Schema

| Table | Description |
|-------|-------------|
| Department | College departments |
| Faculty | Faculty coordinators |
| Student | Registered students |
| Company | Companies offering internships |
| Internship | Internship listings |
| Application | Student internship applications |
| Users | Login credentials with roles |

## User Roles

| Role | Access |
|------|--------|
| Student | Browse internships, apply, track status |
| Faculty | Monitor applications and internships |
| Admin | Full access — manage all records and statuses |