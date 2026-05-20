# Forensic Medicine Department Database System

This project is now structured as a local full-stack database assignment project using:

- MySQL for the main database
- Flask for the backend
- HTML, CSS, and JavaScript templates for the frontend

## Folder Structure

```text
Forensic/
  codes/
    Backend/
      app.py
      run_server.py
      requirements.txt
    Frontend/
      templates/
      static/
  data/
    mysql_forensic_database.sql
    sqlite_schema.sql
    sqlite_seed.sql
  docs/
    DATABASE_DESIGN.md
  backups/
  logs/
  tests/
  start.ps1
  start.bat
  start.sh
```

## Step 1: Start MySQL

If your MySQL service is named `MySQL80`, run PowerShell as Administrator and use:

```powershell
net start MySQL80
```

If it is already running, you can skip this step.

## Step 2: Create the Database in MySQL

Open MySQL Workbench or MySQL CLI as a user with permission to create databases and users.

Copy-paste and run the full script:

```text
X:\Forensic\data\mysql_forensic_database.sql
```

That script creates:

- Database: `forensic_medicine_db`
- MySQL app user: `forensic_user`
- Password: `forensic123`
- All tables, relationships, indexes, views, and sample records

## Step 3: Install Backend Requirements

```powershell
cd X:\Forensic
python -m pip install -r codes\Backend\requirements.txt
```

## Step 4: Start the Backend and Frontend

The frontend is served by Flask from `codes/Frontend`, so you only need one app server:

```powershell
cd X:\Forensic
.\start.ps1
```

Or:

```powershell
python codes\Backend\run_server.py
```

Then open:

```text
http://127.0.0.1:5000/login
```

## Demo Logins

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `admin` | `admin123` |
| Doctor / JMO | `doctor` | `doctor123` |
| Clerical officer | `clerk` | `clerk123` |
| Laboratory staff | `lab` | `lab123` |
| Research view | `researcher` | `research123` |

## What to Demonstrate

- MySQL relational schema with primary keys, foreign keys, indexes, views, and constraints.
- Patient registration and search.
- Clinical MLEF case records.
- Autopsy PMR and cause-of-death tracking.
- Evidence tracking and chain of custody.
- Lab investigations.
- Court reports and printable medico-legal reports.
- Role-based access control.
- Audit logs.
- Daily/monthly SQL reports and CSV exports.
- MySQL backup from the admin backup page.

## Local Runtime Flow

```text
MySQL Server
  -> forensic_medicine_db
  -> Flask backend in codes/Backend
  -> Frontend templates/static files in codes/Frontend
  -> Web browser at http://127.0.0.1:5000
```

## SQLite Files

`data/sqlite_schema.sql` and `data/sqlite_seed.sql` are kept only for automated tests and fallback development. The assignment/demo database is MySQL.
