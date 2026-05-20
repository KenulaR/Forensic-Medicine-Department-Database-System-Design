# Forensic Medicine Department Database System

The Forensic Medicine Department Database System is a local full-stack database application designed to modernize record management in a forensic medical department. The system replaces manual, paper-based record keeping with a structured digital platform for managing patients, medico-legal cases, clinical MLEF records, autopsy PMR records, evidence, laboratory investigations, documents, court reports, staff, users, audit logs, and statistical reports.

Built around a normalized MySQL relational database, the project focuses on strong database design, referential integrity, role-based access control, and practical reporting workflows required in a forensic medicine environment. The system supports both clinical forensic work and autopsy/postmortem work, allowing department staff to retrieve case records quickly, track evidence responsibly, monitor pending reports, and generate useful medico-legal outputs.

This repository is organized as a database module mini project with a clear separation between backend source code, frontend templates, SQL database scripts, documentation, and local deployment utilities.

## Repository Structure

```text
codes/Backend - Flask backend for authentication, CRUD workflows, reports, audit logging, MySQL access, and backup handling
codes/Frontend - HTML, CSS, JavaScript, and Jinja templates for dashboards, forms, record views, reports, and administration
data - MySQL database creation script, sample data, and SQLite fallback files for automated testing
docs - database design documentation and ER/database explanation material
tests - automated backend tests using SQLite test mode
backups - local database backup output folder
logs - local server log output folder
```

## Current Implementation Snapshot

- MySQL relational schema with primary keys, foreign keys, unique constraints, indexes, views, controlled values, and sample data.
- User authentication with hashed passwords, session handling, CSRF protection, and role-based access controls.
- Patient registration, search, update, and case linkage.
- Clinical forensic case workflow with MLEF records, examination findings, investigations, referrals, police copy status, MLR tracking, and court dates.
- Autopsy/postmortem workflow with PMR records, inquest/court order details, pre-autopsy information, findings, cause-of-death tracking, histology status, and court dates.
- Evidence management with evidence codes, storage locations, lab status, printable label/barcode page, and chain-of-custody tracking.
- Laboratory test management for toxicology, histology, DNA, swabs, X-ray/CT, and other investigations.
- Document registry for MLEF copies, court orders, inquest orders, PMR scans, COD forms, summons, receipts, photographs, and issued reports.
- Court report management with printable medico-legal report pages.
- Dashboard analytics, daily case report, monthly statistics, pending report view, CSV export, notifications, and audit logs.
- Local backup and restore concept through the admin interface.

## Technology Stack

| Layer | Technology |
| --- | --- |
| Database | MySQL 8+ |
| Backend | Python Flask |
| Database Driver | PyMySQL |
| Frontend | HTML, CSS, JavaScript, Jinja templates |
| Testing | Pytest, SQLite fallback mode |

## Getting Started

### 1. Start MySQL

If the MySQL service is named `MySQL80`, run PowerShell as Administrator:

```powershell
net start MySQL80
```

### 2. Create the Database

Open MySQL Workbench or the MySQL CLI and run the full script:

```text
data/mysql_forensic_database.sql
```

The script creates:

- Database: `forensic_medicine_db`
- Application user: `forensic_user`
- Password: `forensic123`
- Tables, relationships, indexes, views, and sample records

### 3. Install Backend Requirements

```powershell
cd X:\Forensic
python -m pip install -r codes\Backend\requirements.txt
```

### 4. Start the Local Application

```powershell
cd X:\Forensic
.\start.ps1
```

Then open:

```text
http://127.0.0.1:5000/login
```

## Demo Accounts

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `admin` | `admin123` |
| Doctor / JMO | `doctor` | `doctor123` |
| Clerical Officer | `clerk` | `clerk123` |
| Laboratory Staff | `lab` | `lab123` |
| Research View | `researcher` | `research123` |

## Database Design Focus

The database is the central part of this project. The design separates patient records, forensic cases, clinical examinations, postmortems, evidence, custody movements, lab tests, documents, reports, staff, users, notifications, and audit logs into normalized relational tables.

Important database features include:

- One-to-many and one-to-one relationships modeled with foreign keys.
- Separate clinical and autopsy tables to avoid mixing unrelated attributes.
- Chain-of-custody table to preserve multiple evidence movement records.
- SQL views for case directories, pending reports, daily reports, and monthly statistics.
- Indexes for commonly searched fields such as case, patient, MLEF, PMR, evidence, report, and audit records.
- Controlled values using MySQL `ENUM` columns.

Full design guidance is available in:

```text
DESIGN.md
docs/DATABASE_DESIGN.md
```

## Local Runtime Flow

```text
MySQL Server
  -> forensic_medicine_db
  -> Flask backend in codes/Backend
  -> Frontend templates and static files in codes/Frontend
  -> Web browser at http://127.0.0.1:5000
```

## Team

| Registration No. | Name |
| --- | --- |
| E/23/299 | R.D.K.D. Ranasinghe |
| E/23/084 | D.R.C.V. Dissanayake |
| E/23/292 | K.S. Rambukkanage |
| E/23/302 | T.G.D. Randeep |

## Links

- Project Repository: [Forensic Medicine Department Database System](https://github.com/KenulaR/Forensic-Medicine-Department-Database-System-Design)
- Department of Computer Engineering: https://ce.pdn.ac.lk/
- University of Peradeniya: https://www.pdn.ac.lk/
