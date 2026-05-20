from __future__ import annotations

import csv
import io
import os
import secrets
import shutil
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    g,
    current_app,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[1] if BASE_DIR.name == "Backend" and BASE_DIR.parent.name == "codes" else BASE_DIR
FRONTEND_DIR = PROJECT_ROOT / "codes" / "Frontend"
if FRONTEND_DIR.exists():
    TEMPLATE_DIR = FRONTEND_DIR / "templates"
    STATIC_DIR = FRONTEND_DIR / "static"
else:
    TEMPLATE_DIR = PROJECT_ROOT / "templates"
    STATIC_DIR = PROJECT_ROOT / "static"
DATA_DIR = PROJECT_ROOT / "data"

CHOICES = {
    "gender": ["Female", "Male", "Other", "Unknown"],
    "case_category": ["Clinical", "Autopsy"],
    "case_type": [
        "Trauma patient",
        "Domestic abuse",
        "Sexual abuse",
        "Child abuse",
        "Detainee examination",
        "Drug addiction",
        "Age estimation",
        "DNA sample",
        "Hospital death",
        "Outside death",
        "High profile death",
        "Other",
    ],
    "authorization_type": ["MLEF", "Request Letter", "Court Order", "Inquest Order", "Other"],
    "case_status": ["Open", "In Review", "Report Pending", "Closed", "Archived"],
    "mlr_status": ["Pending", "Drafted", "Issued"],
    "death_type": ["Natural", "Accidental", "Suicidal", "Homicidal", "Undetermined"],
    "cod_status": ["Pending", "Drafted", "Issued"],
    "histology_status": ["Not Required", "Pending", "Received"],
    "document_type": [
        "MLEF Doctor Copy",
        "Photo",
        "Investigation",
        "Referral Report",
        "Summons",
        "Issued Report Copy",
        "Certificate Receipt",
        "Court Order",
        "Inquest Order",
        "PMR Scan",
        "COD Form",
        "Other",
    ],
    "evidence_type": [
        "Blood sample",
        "Urine sample",
        "Swab",
        "Clothing",
        "Weapon/object",
        "Histology tissue block",
        "Photo media",
        "Other",
    ],
    "lab_status": ["Not Sent", "Pending", "Completed", "Returned"],
    "custody_action": ["Collected", "Transferred", "Stored", "Tested", "Returned", "Disposed"],
    "test_type": ["X-ray/CT", "Blood toxicology", "Urine toxicology", "Swab analysis", "Histology", "DNA", "Other"],
    "test_status": ["Requested", "In Progress", "Completed", "Cancelled"],
    "report_type": ["MLR", "PMR", "COD", "Court Submission", "Research Summary", "Other"],
    "report_status": ["Requested", "Drafting", "Submitted", "Closed"],
    "staff_role": [
        "Judicial Medical Officer",
        "Doctor",
        "Laboratory Staff",
        "Clerical Officer",
        "Administrator",
    ],
    "user_role": ["admin", "doctor", "clerk", "lab", "researcher"],
}

MODULES = {
    "patients": {
        "label": "Patients",
        "singular": "Patient",
        "table": "patients",
        "read_roles": ("admin", "doctor", "clerk", "lab", "researcher"),
        "write_roles": ("admin", "doctor", "clerk"),
        "columns": ["Patient No", "Name", "Gender", "Age", "Contact", "Created"],
        "list_sql": """
            SELECT id, patient_no AS "Patient No", full_name AS "Name", gender AS "Gender",
                   age AS "Age", contact_no AS "Contact", date(created_at) AS "Created"
            FROM patients
            ORDER BY created_at DESC
        """,
        "search_sql": """
            SELECT id, patient_no AS "Patient No", full_name AS "Name", gender AS "Gender",
                   age AS "Age", contact_no AS "Contact", date(created_at) AS "Created"
            FROM patients
            WHERE patient_no LIKE ? OR full_name LIKE ? OR nic LIKE ? OR contact_no LIKE ?
            ORDER BY created_at DESC
        """,
        "search_params": 4,
        "fields": [
            {"name": "patient_no", "label": "Patient No", "required": True},
            {"name": "full_name", "label": "Full Name", "required": True},
            {"name": "nic", "label": "NIC / Identifier"},
            {"name": "dob", "label": "Date of Birth", "type": "date"},
            {"name": "age", "label": "Age", "type": "number"},
            {"name": "gender", "label": "Gender", "type": "select", "choices": "gender", "required": True},
            {"name": "address", "label": "Address", "type": "textarea"},
            {"name": "contact_no", "label": "Contact No"},
            {"name": "guardian_name", "label": "Guardian / Next of Kin"},
        ],
    },
    "cases": {
        "label": "Cases",
        "singular": "Case",
        "table": "forensic_cases",
        "read_roles": ("admin", "doctor", "clerk", "lab", "researcher"),
        "write_roles": ("admin", "doctor", "clerk"),
        "detail_endpoint": "case_detail",
        "columns": ["Case No", "Category", "Type", "Patient", "Doctor", "Status"],
        "list_sql": """
            SELECT id, case_no AS "Case No", case_category AS "Category", case_type AS "Type",
                   patient_name AS "Patient", assigned_doctor AS "Doctor", status AS "Status"
            FROM v_case_directory
            ORDER BY id DESC
        """,
        "search_sql": """
            SELECT id, case_no AS "Case No", case_category AS "Category", case_type AS "Type",
                   patient_name AS "Patient", assigned_doctor AS "Doctor", status AS "Status"
            FROM v_case_directory
            WHERE case_no LIKE ? OR patient_name LIKE ? OR case_type LIKE ? OR authorization_ref LIKE ? OR police_station LIKE ?
            ORDER BY id DESC
        """,
        "search_params": 5,
        "fields": [
            {"name": "case_no", "label": "Case No", "required": True},
            {"name": "patient_id", "label": "Patient", "type": "select", "source": "patients", "required": True},
            {"name": "case_category", "label": "Category", "type": "select", "choices": "case_category", "required": True},
            {"name": "case_type", "label": "Case Type", "type": "select", "choices": "case_type", "required": True},
            {"name": "referral_source", "label": "Referral Source"},
            {"name": "authorization_type", "label": "Legal Authorisation", "type": "select", "choices": "authorization_type", "required": True},
            {"name": "authorization_ref", "label": "Authorisation Ref"},
            {"name": "incident_date", "label": "Incident Date", "type": "date"},
            {"name": "incident_location", "label": "Incident Location"},
            {"name": "police_station", "label": "Police Station"},
            {"name": "assigned_doctor_id", "label": "Assigned Doctor", "type": "select", "source": "doctors"},
            {"name": "status", "label": "Status", "type": "select", "choices": "case_status", "required": True},
            {"name": "summary", "label": "Summary", "type": "textarea"},
        ],
    },
    "clinical": {
        "label": "Clinical MLEF",
        "singular": "Clinical Examination",
        "table": "clinical_examinations",
        "read_roles": ("admin", "doctor", "clerk", "researcher"),
        "write_roles": ("admin", "doctor", "clerk"),
        "columns": ["MLEF No", "Case No", "Patient", "Examined", "MLR", "Court Date"],
        "list_sql": """
            SELECT ce.id, ce.mlef_no AS "MLEF No", c.case_no AS "Case No", p.full_name AS "Patient",
                   ce.examined_at AS "Examined", ce.mlr_status AS "MLR", ce.next_court_date AS "Court Date"
            FROM clinical_examinations ce
            JOIN forensic_cases c ON c.id = ce.case_id
            JOIN patients p ON p.id = c.patient_id
            ORDER BY ce.id DESC
        """,
        "search_sql": """
            SELECT ce.id, ce.mlef_no AS "MLEF No", c.case_no AS "Case No", p.full_name AS "Patient",
                   ce.examined_at AS "Examined", ce.mlr_status AS "MLR", ce.next_court_date AS "Court Date"
            FROM clinical_examinations ce
            JOIN forensic_cases c ON c.id = ce.case_id
            JOIN patients p ON p.id = c.patient_id
            WHERE ce.mlef_no LIKE ? OR c.case_no LIKE ? OR p.full_name LIKE ? OR ce.mlr_status LIKE ?
            ORDER BY ce.id DESC
        """,
        "search_params": 4,
        "fields": [
            {"name": "case_id", "label": "Clinical Case", "type": "select", "source": "clinical_cases", "required": True},
            {"name": "mlef_no", "label": "MLEF No", "required": True},
            {"name": "examined_at", "label": "Examined At", "type": "datetime-local"},
            {"name": "history", "label": "History", "type": "textarea"},
            {"name": "findings", "label": "Findings", "type": "textarea"},
            {"name": "injuries", "label": "Injuries", "type": "textarea"},
            {"name": "investigation_findings", "label": "Investigation Findings", "type": "textarea"},
            {"name": "referral_notes", "label": "Referral Reports / Notes", "type": "textarea"},
            {"name": "review_notes", "label": "Review Notes", "type": "textarea"},
            {"name": "photos_path", "label": "Photographs Storage Path"},
            {"name": "issued_police_copy", "label": "Police Copy Issued", "type": "checkbox"},
            {"name": "mlr_status", "label": "MLR Status", "type": "select", "choices": "mlr_status", "required": True},
            {"name": "next_court_date", "label": "Next Court Date", "type": "date"},
        ],
    },
    "postmortems": {
        "label": "Postmortems",
        "singular": "Postmortem",
        "table": "postmortems",
        "read_roles": ("admin", "doctor", "clerk", "lab", "researcher"),
        "write_roles": ("admin", "doctor"),
        "columns": ["PMR No", "Case No", "Patient", "Death Type", "COD", "Histology"],
        "list_sql": """
            SELECT pm.id, pm.pmr_no AS "PMR No", c.case_no AS "Case No", p.full_name AS "Patient",
                   pm.death_type AS "Death Type", pm.cod_status AS "COD", pm.histology_status AS "Histology"
            FROM postmortems pm
            JOIN forensic_cases c ON c.id = pm.case_id
            JOIN patients p ON p.id = c.patient_id
            ORDER BY pm.id DESC
        """,
        "search_sql": """
            SELECT pm.id, pm.pmr_no AS "PMR No", c.case_no AS "Case No", p.full_name AS "Patient",
                   pm.death_type AS "Death Type", pm.cod_status AS "COD", pm.histology_status AS "Histology"
            FROM postmortems pm
            JOIN forensic_cases c ON c.id = pm.case_id
            JOIN patients p ON p.id = c.patient_id
            WHERE pm.pmr_no LIKE ? OR c.case_no LIKE ? OR p.full_name LIKE ? OR pm.death_type LIKE ? OR pm.cod_status LIKE ?
            ORDER BY pm.id DESC
        """,
        "search_params": 5,
        "fields": [
            {"name": "case_id", "label": "Autopsy Case", "type": "select", "source": "autopsy_cases", "required": True},
            {"name": "pmr_no", "label": "PMR No", "required": True},
            {"name": "death_type", "label": "Death Type", "type": "select", "choices": "death_type", "required": True},
            {"name": "inquest_order_no", "label": "Inquest / Court Order No"},
            {"name": "autopsy_date", "label": "Autopsy Date", "type": "datetime-local"},
            {"name": "pre_autopsy_info", "label": "Pre-autopsy Information", "type": "textarea"},
            {"name": "external_findings", "label": "External Findings", "type": "textarea"},
            {"name": "internal_findings", "label": "Internal Findings", "type": "textarea"},
            {"name": "cause_of_death", "label": "Cause of Death", "type": "textarea"},
            {"name": "cod_status", "label": "COD Status", "type": "select", "choices": "cod_status", "required": True},
            {"name": "histology_status", "label": "Histology Status", "type": "select", "choices": "histology_status", "required": True},
            {"name": "photos_path", "label": "Photographs Storage Path"},
            {"name": "audio_transcript_ref", "label": "Audio/Text PMR Transcript"},
            {"name": "next_court_date", "label": "Next Court Date", "type": "date"},
        ],
    },
    "documents": {
        "label": "Documents",
        "singular": "Document",
        "table": "documents",
        "read_roles": ("admin", "doctor", "clerk", "researcher"),
        "write_roles": ("admin", "doctor", "clerk"),
        "columns": ["Case No", "Type", "Reference", "Storage", "Received"],
        "list_sql": """
            SELECT d.id, c.case_no AS "Case No", d.document_type AS "Type", d.reference_no AS "Reference",
                   d.storage_ref AS "Storage", d.received_at AS "Received"
            FROM documents d
            JOIN forensic_cases c ON c.id = d.case_id
            ORDER BY d.id DESC
        """,
        "search_sql": """
            SELECT d.id, c.case_no AS "Case No", d.document_type AS "Type", d.reference_no AS "Reference",
                   d.storage_ref AS "Storage", d.received_at AS "Received"
            FROM documents d
            JOIN forensic_cases c ON c.id = d.case_id
            WHERE c.case_no LIKE ? OR d.document_type LIKE ? OR d.reference_no LIKE ? OR d.storage_ref LIKE ?
            ORDER BY d.id DESC
        """,
        "search_params": 4,
        "fields": [
            {"name": "case_id", "label": "Case", "type": "select", "source": "cases", "required": True},
            {"name": "document_type", "label": "Document Type", "type": "select", "choices": "document_type", "required": True},
            {"name": "reference_no", "label": "Reference No"},
            {"name": "storage_ref", "label": "Storage Reference"},
            {"name": "received_at", "label": "Received At", "type": "date"},
            {"name": "issued_to", "label": "Issued To"},
            {"name": "notes", "label": "Notes", "type": "textarea"},
        ],
    },
    "evidence": {
        "label": "Evidence",
        "singular": "Evidence",
        "table": "evidence",
        "read_roles": ("admin", "doctor", "clerk", "lab", "researcher"),
        "write_roles": ("admin", "doctor", "lab"),
        "detail_endpoint": "evidence_detail",
        "columns": ["Code", "Case No", "Type", "Storage", "Lab Status"],
        "list_sql": """
            SELECT e.id, e.evidence_code AS "Code", c.case_no AS "Case No", e.evidence_type AS "Type",
                   e.storage_location AS "Storage", e.lab_status AS "Lab Status"
            FROM evidence e
            JOIN forensic_cases c ON c.id = e.case_id
            ORDER BY e.id DESC
        """,
        "search_sql": """
            SELECT e.id, e.evidence_code AS "Code", c.case_no AS "Case No", e.evidence_type AS "Type",
                   e.storage_location AS "Storage", e.lab_status AS "Lab Status"
            FROM evidence e
            JOIN forensic_cases c ON c.id = e.case_id
            WHERE e.evidence_code LIKE ? OR c.case_no LIKE ? OR e.evidence_type LIKE ? OR e.storage_location LIKE ?
            ORDER BY e.id DESC
        """,
        "search_params": 4,
        "fields": [
            {"name": "evidence_code", "label": "Evidence Code", "required": True},
            {"name": "case_id", "label": "Case", "type": "select", "source": "cases", "required": True},
            {"name": "evidence_type", "label": "Evidence Type", "type": "select", "choices": "evidence_type", "required": True},
            {"name": "description", "label": "Description", "type": "textarea"},
            {"name": "collected_at", "label": "Collected At", "type": "datetime-local"},
            {"name": "collected_by_staff_id", "label": "Collected By", "type": "select", "source": "staff"},
            {"name": "storage_location", "label": "Storage Location"},
            {"name": "lab_status", "label": "Lab Status", "type": "select", "choices": "lab_status", "required": True},
            {"name": "barcode_value", "label": "Barcode / QR Value"},
        ],
    },
    "lab-tests": {
        "label": "Lab Tests",
        "singular": "Lab Test",
        "table": "lab_tests",
        "read_roles": ("admin", "doctor", "lab", "researcher"),
        "write_roles": ("admin", "doctor", "lab"),
        "columns": ["Test Code", "Case No", "Evidence", "Type", "Status", "Report Ref"],
        "list_sql": """
            SELECT lt.id, lt.test_code AS "Test Code", c.case_no AS "Case No",
                   COALESCE(e.evidence_code, '-') AS "Evidence", lt.test_type AS "Type",
                   lt.status AS "Status", lt.report_ref AS "Report Ref"
            FROM lab_tests lt
            JOIN forensic_cases c ON c.id = lt.case_id
            LEFT JOIN evidence e ON e.id = lt.evidence_id
            ORDER BY lt.id DESC
        """,
        "search_sql": """
            SELECT lt.id, lt.test_code AS "Test Code", c.case_no AS "Case No",
                   COALESCE(e.evidence_code, '-') AS "Evidence", lt.test_type AS "Type",
                   lt.status AS "Status", lt.report_ref AS "Report Ref"
            FROM lab_tests lt
            JOIN forensic_cases c ON c.id = lt.case_id
            LEFT JOIN evidence e ON e.id = lt.evidence_id
            WHERE lt.test_code LIKE ? OR c.case_no LIKE ? OR e.evidence_code LIKE ? OR lt.test_type LIKE ? OR lt.status LIKE ?
            ORDER BY lt.id DESC
        """,
        "search_params": 5,
        "fields": [
            {"name": "test_code", "label": "Test Code", "required": True},
            {"name": "case_id", "label": "Case", "type": "select", "source": "cases", "required": True},
            {"name": "evidence_id", "label": "Evidence", "type": "select", "source": "evidence"},
            {"name": "test_type", "label": "Test Type", "type": "select", "choices": "test_type", "required": True},
            {"name": "requested_at", "label": "Requested At", "type": "datetime-local"},
            {"name": "requested_by_staff_id", "label": "Requested By", "type": "select", "source": "staff"},
            {"name": "result", "label": "Result", "type": "textarea"},
            {"name": "status", "label": "Status", "type": "select", "choices": "test_status", "required": True},
            {"name": "report_ref", "label": "Report Reference"},
        ],
    },
    "reports": {
        "label": "Court Reports",
        "singular": "Court Report",
        "table": "court_reports",
        "read_roles": ("admin", "doctor", "clerk", "researcher"),
        "write_roles": ("admin", "doctor", "clerk"),
        "detail_endpoint": "report_print",
        "columns": ["Report No", "Case No", "Type", "Status", "Due", "Prepared By"],
        "list_sql": """
            SELECT r.id, r.report_no AS "Report No", c.case_no AS "Case No", r.report_type AS "Type",
                   r.status AS "Status", r.due_date AS "Due", s.full_name AS "Prepared By"
            FROM court_reports r
            JOIN forensic_cases c ON c.id = r.case_id
            LEFT JOIN staff s ON s.id = r.prepared_by_staff_id
            ORDER BY r.id DESC
        """,
        "search_sql": """
            SELECT r.id, r.report_no AS "Report No", c.case_no AS "Case No", r.report_type AS "Type",
                   r.status AS "Status", r.due_date AS "Due", s.full_name AS "Prepared By"
            FROM court_reports r
            JOIN forensic_cases c ON c.id = r.case_id
            LEFT JOIN staff s ON s.id = r.prepared_by_staff_id
            WHERE r.report_no LIKE ? OR c.case_no LIKE ? OR r.report_type LIKE ? OR r.status LIKE ? OR r.requested_by LIKE ?
            ORDER BY r.id DESC
        """,
        "search_params": 5,
        "fields": [
            {"name": "report_no", "label": "Report No", "required": True},
            {"name": "case_id", "label": "Case", "type": "select", "source": "cases", "required": True},
            {"name": "report_type", "label": "Report Type", "type": "select", "choices": "report_type", "required": True},
            {"name": "requested_by", "label": "Requested By"},
            {"name": "requested_at", "label": "Requested At", "type": "date"},
            {"name": "due_date", "label": "Due Date", "type": "date"},
            {"name": "submission_date", "label": "Submission Date", "type": "date"},
            {"name": "status", "label": "Status", "type": "select", "choices": "report_status", "required": True},
            {"name": "prepared_by_staff_id", "label": "Prepared By", "type": "select", "source": "doctors"},
            {"name": "summary", "label": "Summary", "type": "textarea"},
            {"name": "digital_signature", "label": "Digital Signature"},
        ],
    },
    "staff": {
        "label": "Staff",
        "singular": "Staff Member",
        "table": "staff",
        "read_roles": ("admin", "doctor", "clerk"),
        "write_roles": ("admin",),
        "columns": ["Code", "Name", "Role", "Specialization", "Contact", "Active"],
        "list_sql": """
            SELECT id, staff_code AS "Code", full_name AS "Name", staff_role AS "Role",
                   specialization AS "Specialization", contact_no AS "Contact",
                   CASE active WHEN 1 THEN 'Yes' ELSE 'No' END AS "Active"
            FROM staff
            ORDER BY full_name
        """,
        "search_sql": """
            SELECT id, staff_code AS "Code", full_name AS "Name", staff_role AS "Role",
                   specialization AS "Specialization", contact_no AS "Contact",
                   CASE active WHEN 1 THEN 'Yes' ELSE 'No' END AS "Active"
            FROM staff
            WHERE staff_code LIKE ? OR full_name LIKE ? OR staff_role LIKE ? OR specialization LIKE ?
            ORDER BY full_name
        """,
        "search_params": 4,
        "fields": [
            {"name": "staff_code", "label": "Staff Code", "required": True},
            {"name": "full_name", "label": "Full Name", "required": True},
            {"name": "staff_role", "label": "Role", "type": "select", "choices": "staff_role", "required": True},
            {"name": "specialization", "label": "Specialization"},
            {"name": "contact_no", "label": "Contact No"},
            {"name": "email", "label": "Email", "type": "email"},
            {"name": "active", "label": "Active", "type": "checkbox"},
        ],
    },
}


NAV_GROUPS = [
    ("Operations", ["patients", "cases", "clinical", "postmortems"]),
    ("Evidence", ["evidence", "lab-tests", "documents"]),
    ("Reporting", ["reports"]),
    ("Administration", ["staff"]),
]


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        instance_relative_config=False,
        template_folder=str(TEMPLATE_DIR),
        static_folder=str(STATIC_DIR),
        static_url_path="/static",
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FORENSIC_SECRET_KEY", "dev-local-change-me"),
        DB_ENGINE=os.environ.get("FORENSIC_DB_ENGINE", "mysql").lower(),
        DATABASE=str(DATA_DIR / "forensic.db"),
        MYSQL_HOST=os.environ.get("FORENSIC_MYSQL_HOST", "127.0.0.1"),
        MYSQL_PORT=int(os.environ.get("FORENSIC_MYSQL_PORT", "3306")),
        MYSQL_USER=os.environ.get("FORENSIC_MYSQL_USER", "forensic_user"),
        MYSQL_PASSWORD=os.environ.get("FORENSIC_MYSQL_PASSWORD", "forensic123"),
        MYSQL_DATABASE=os.environ.get("FORENSIC_MYSQL_DATABASE", "forensic_medicine_db"),
        BACKUP_FOLDER=str(PROJECT_ROOT / "backups"),
        CSRF_ENABLED=True,
    )
    if test_config:
        app.config.update(test_config)

    @app.before_request
    def load_user_and_check_csrf():
        user_id = session.get("user_id")
        g.user = None
        if user_id:
            g.user = get_db().execute(
                """
                SELECT u.*, s.full_name AS staff_name, s.staff_role
                FROM users u
                LEFT JOIN staff s ON s.id = u.staff_id
                WHERE u.id = ? AND u.is_active = 1
                """,
                (user_id,),
            ).fetchone()
        if app.config.get("CSRF_ENABLED", True) and request.method == "POST":
            expected = session.get("_csrf_token")
            supplied = request.form.get("_csrf_token")
            if not expected or not supplied or not secrets.compare_digest(expected, supplied):
                abort(400, "Invalid form token")

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    app.jinja_env.globals.update(
        csrf_token=csrf_token,
        current_user=lambda: g.get("user"),
        has_role=has_role,
        nav_groups=visible_nav_groups,
        module_url=lambda key: url_for("module_list", module_key=key),
    )

    @app.route("/")
    @login_required
    def dashboard():
        db = get_db()
        stats = {
            "patients": db.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
            "cases": db.execute("SELECT COUNT(*) FROM forensic_cases").fetchone()[0],
            "clinical": db.execute("SELECT COUNT(*) FROM forensic_cases WHERE case_category = 'Clinical'").fetchone()[0],
            "autopsy": db.execute("SELECT COUNT(*) FROM forensic_cases WHERE case_category = 'Autopsy'").fetchone()[0],
            "pending_reports": db.execute("SELECT COUNT(*) FROM v_pending_reports").fetchone()[0],
            "pending_lab": db.execute("SELECT COUNT(*) FROM lab_tests WHERE status IN ('Requested', 'In Progress')").fetchone()[0],
        }
        case_mix = db.execute(
            """
            SELECT case_category, COUNT(*) AS total
            FROM forensic_cases
            GROUP BY case_category
            ORDER BY case_category
            """
        ).fetchall()
        report_status = db.execute(
            """
            SELECT status, COUNT(*) AS total
            FROM court_reports
            GROUP BY status
            ORDER BY status
            """
        ).fetchall()
        alerts = db.execute(
            """
            SELECT id, title, message, due_date, case_id
            FROM notifications
            WHERE status = 'Open'
            ORDER BY due_date IS NULL, due_date ASC, created_at DESC
            LIMIT 6
            """
        ).fetchall()
        recent_cases = db.execute(
            """
            SELECT id, case_no, case_category, case_type, patient_name, status
            FROM v_case_directory
            ORDER BY id DESC
            LIMIT 6
            """
        ).fetchall()
        audit = db.execute(
            """
            SELECT a.created_at, a.action, a.entity, a.details, u.username
            FROM audit_logs a
            LEFT JOIN users u ON u.id = a.actor_user_id
            ORDER BY a.id DESC
            LIMIT 8
            """
        ).fetchall()
        return render_template(
            "dashboard.html",
            stats=stats,
            case_mix=case_mix,
            report_status=report_status,
            alerts=alerts,
            recent_cases=recent_cases,
            audit=audit,
        )

    @app.route("/login", methods=("GET", "POST"))
    def login():
        if g.get("user"):
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = get_db().execute(
                "SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)
            ).fetchone()
            if user and check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_id"] = user["id"]
                get_db().execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user["id"]),
                )
                get_db().commit()
                log_audit("login", "users", user["id"], f"{username} signed in")
                return redirect(url_for("dashboard"))
            flash("Invalid username or password.", "danger")
        return render_template("login.html")

    @app.route("/logout", methods=("POST",))
    @login_required
    def logout():
        log_audit("logout", "users", g.user["id"], f"{g.user['username']} signed out")
        session.clear()
        flash("Signed out.", "success")
        return redirect(url_for("login"))

    @app.route("/records/<module_key>")
    @login_required
    def module_list(module_key: str):
        config = get_module(module_key)
        require_roles(*config["read_roles"])
        q = request.args.get("q", "").strip()
        db = get_db()
        if q and config.get("search_sql"):
            rows = db.execute(config["search_sql"], tuple([f"%{q}%"] * config["search_params"])).fetchall()
        else:
            rows = db.execute(config["list_sql"]).fetchall()
        return render_template(
            "list.html",
            module_key=module_key,
            config=config,
            rows=rows,
            columns=config["columns"],
            q=q,
            can_write=has_role(*config["write_roles"]),
        )

    @app.route("/records/<module_key>/new", methods=("GET", "POST"))
    @login_required
    def module_new(module_key: str):
        config = get_module(module_key)
        require_roles(*config["write_roles"])
        values = default_values(config["fields"])
        for field in config["fields"]:
            if field["name"] in request.args:
                values[field["name"]] = request.args.get(field["name"])
        if request.method == "POST":
            values = collect_form_values(config["fields"])
            errors = validate_values(config["fields"], values)
            if not errors:
                item_id = insert_record(config["table"], values)
                if module_key == "evidence" and not values.get("barcode_value"):
                    update_barcode_value(item_id)
                log_audit("create", config["table"], item_id, f"Created {config['singular']}")
                flash(f"{config['singular']} created.", "success")
                return redirect_after_save(module_key, item_id)
            for error in errors:
                flash(error, "danger")
        return render_template(
            "form.html",
            title=f"New {config['singular']}",
            fields=prepare_fields(config["fields"]),
            values=values,
            action_url=url_for("module_new", module_key=module_key),
            cancel_url=url_for("module_list", module_key=module_key),
        )

    @app.route("/records/<module_key>/<int:item_id>/edit", methods=("GET", "POST"))
    @login_required
    def module_edit(module_key: str, item_id: int):
        config = get_module(module_key)
        require_roles(*config["write_roles"])
        row = get_db().execute(f"SELECT * FROM {config['table']} WHERE id = ?", (item_id,)).fetchone()
        if not row:
            abort(404)
        values = dict(row)
        if request.method == "POST":
            values = collect_form_values(config["fields"])
            errors = validate_values(config["fields"], values)
            if not errors:
                update_record(config["table"], item_id, values)
                if module_key == "evidence" and not values.get("barcode_value"):
                    update_barcode_value(item_id)
                log_audit("update", config["table"], item_id, f"Updated {config['singular']}")
                flash(f"{config['singular']} updated.", "success")
                return redirect_after_save(module_key, item_id)
            for error in errors:
                flash(error, "danger")
        return render_template(
            "form.html",
            title=f"Edit {config['singular']}",
            fields=prepare_fields(config["fields"]),
            values=values,
            action_url=url_for("module_edit", module_key=module_key, item_id=item_id),
            cancel_url=url_for("module_list", module_key=module_key),
        )

    @app.route("/records/<module_key>/<int:item_id>/delete", methods=("POST",))
    @login_required
    def module_delete(module_key: str, item_id: int):
        config = get_module(module_key)
        require_roles(*config["write_roles"])
        db = get_db()
        row = db.execute(f"SELECT id FROM {config['table']} WHERE id = ?", (item_id,)).fetchone()
        if not row:
            abort(404)
        db.execute(f"DELETE FROM {config['table']} WHERE id = ?", (item_id,))
        db.commit()
        log_audit("delete", config["table"], item_id, f"Deleted {config['singular']}")
        flash(f"{config['singular']} deleted.", "success")
        return redirect(url_for("module_list", module_key=module_key))

    @app.route("/cases/<int:case_id>")
    @login_required
    def case_detail(case_id: int):
        require_roles("admin", "doctor", "clerk", "lab", "researcher")
        db = get_db()
        case = db.execute(
            """
            SELECT c.*, p.patient_no, p.full_name AS patient_name, p.gender, p.age, p.address,
                   s.full_name AS assigned_doctor
            FROM forensic_cases c
            JOIN patients p ON p.id = c.patient_id
            LEFT JOIN staff s ON s.id = c.assigned_doctor_id
            WHERE c.id = ?
            """,
            (case_id,),
        ).fetchone()
        if not case:
            abort(404)
        related = {
            "clinical": db.execute("SELECT * FROM clinical_examinations WHERE case_id = ?", (case_id,)).fetchone(),
            "postmortem": db.execute("SELECT * FROM postmortems WHERE case_id = ?", (case_id,)).fetchone(),
            "documents": db.execute("SELECT * FROM documents WHERE case_id = ? ORDER BY id DESC", (case_id,)).fetchall(),
            "evidence": db.execute("SELECT * FROM evidence WHERE case_id = ? ORDER BY id DESC", (case_id,)).fetchall(),
            "lab_tests": db.execute("SELECT * FROM lab_tests WHERE case_id = ? ORDER BY id DESC", (case_id,)).fetchall(),
            "reports": db.execute("SELECT * FROM court_reports WHERE case_id = ? ORDER BY id DESC", (case_id,)).fetchall(),
        }
        return render_template("case_detail.html", case=case, related=related)

    @app.route("/evidence/<int:evidence_id>")
    @login_required
    def evidence_detail(evidence_id: int):
        require_roles("admin", "doctor", "clerk", "lab", "researcher")
        db = get_db()
        evidence = db.execute(
            """
            SELECT e.*, c.case_no, p.full_name AS patient_name, s.full_name AS collected_by
            FROM evidence e
            JOIN forensic_cases c ON c.id = e.case_id
            JOIN patients p ON p.id = c.patient_id
            LEFT JOIN staff s ON s.id = e.collected_by_staff_id
            WHERE e.id = ?
            """,
            (evidence_id,),
        ).fetchone()
        if not evidence:
            abort(404)
        custody = db.execute(
            """
            SELECT cc.*, s.full_name AS handled_by
            FROM chain_of_custody cc
            LEFT JOIN staff s ON s.id = cc.handled_by_staff_id
            WHERE cc.evidence_id = ?
            ORDER BY cc.action_at DESC, cc.id DESC
            """,
            (evidence_id,),
        ).fetchall()
        return render_template(
            "evidence_detail.html",
            evidence=evidence,
            custody=custody,
            staff_options=source_options("staff"),
            action_choices=CHOICES["custody_action"],
            can_write=has_role("admin", "doctor", "lab"),
        )

    @app.route("/evidence/<int:evidence_id>/custody", methods=("POST",))
    @login_required
    def add_custody(evidence_id: int):
        require_roles("admin", "doctor", "lab")
        db = get_db()
        evidence = db.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,)).fetchone()
        if not evidence:
            abort(404)
        values = {
            "evidence_id": evidence_id,
            "action": request.form.get("action"),
            "from_holder": request.form.get("from_holder"),
            "to_holder": request.form.get("to_holder"),
            "handled_by_staff_id": request.form.get("handled_by_staff_id") or None,
            "action_at": normalize_datetime(request.form.get("action_at")),
            "location": request.form.get("location"),
            "notes": request.form.get("notes"),
        }
        if not values["action"] or not values["to_holder"] or not values["action_at"]:
            flash("Action, to holder, and action time are required.", "danger")
            return redirect(url_for("evidence_detail", evidence_id=evidence_id))
        insert_record("chain_of_custody", values)
        log_audit("custody", "evidence", evidence_id, f"Recorded custody movement for {evidence['evidence_code']}")
        flash("Custody movement recorded.", "success")
        return redirect(url_for("evidence_detail", evidence_id=evidence_id))

    @app.route("/evidence/<int:evidence_id>/label")
    @login_required
    def evidence_label(evidence_id: int):
        require_roles("admin", "doctor", "lab", "clerk")
        evidence = get_db().execute(
            """
            SELECT e.*, c.case_no
            FROM evidence e
            JOIN forensic_cases c ON c.id = e.case_id
            WHERE e.id = ?
            """,
            (evidence_id,),
        ).fetchone()
        if not evidence:
            abort(404)
        return render_template("evidence_label.html", evidence=evidence, bars=barcode_bars(evidence["barcode_value"] or evidence["evidence_code"]))

    @app.route("/reports/<int:report_id>/print")
    @login_required
    def report_print(report_id: int):
        require_roles("admin", "doctor", "clerk", "researcher")
        db = get_db()
        report = db.execute(
            """
            SELECT r.*, c.case_no, c.case_category, c.case_type, c.incident_date,
                   c.incident_location, c.police_station, p.patient_no, p.full_name AS patient_name,
                   p.gender, p.age, s.full_name AS prepared_by
            FROM court_reports r
            JOIN forensic_cases c ON c.id = r.case_id
            JOIN patients p ON p.id = c.patient_id
            LEFT JOIN staff s ON s.id = r.prepared_by_staff_id
            WHERE r.id = ?
            """,
            (report_id,),
        ).fetchone()
        if not report:
            abort(404)
        clinical = db.execute("SELECT * FROM clinical_examinations WHERE case_id = ?", (report["case_id"],)).fetchone()
        postmortem = db.execute("SELECT * FROM postmortems WHERE case_id = ?", (report["case_id"],)).fetchone()
        evidence = db.execute("SELECT * FROM evidence WHERE case_id = ? ORDER BY id", (report["case_id"],)).fetchall()
        return render_template("report_print.html", report=report, clinical=clinical, postmortem=postmortem, evidence=evidence)

    @app.route("/analytics")
    @login_required
    def analytics():
        require_roles("admin", "doctor", "clerk", "lab", "researcher")
        db = get_db()
        daily = db.execute("SELECT * FROM v_daily_case_report ORDER BY case_date DESC, case_category").fetchall()
        monthly = db.execute("SELECT * FROM v_monthly_statistics ORDER BY case_month DESC, case_category, case_type").fetchall()
        pending = db.execute("SELECT * FROM v_pending_reports ORDER BY due_date").fetchall()
        lab = db.execute(
            """
            SELECT status, COUNT(*) AS total
            FROM lab_tests
            GROUP BY status
            ORDER BY status
            """
        ).fetchall()
        deaths = db.execute(
            """
            SELECT death_type, COUNT(*) AS total
            FROM postmortems
            GROUP BY death_type
            ORDER BY death_type
            """
        ).fetchall()
        return render_template("analytics.html", daily=daily, monthly=monthly, pending=pending, lab=lab, deaths=deaths)

    @app.route("/analytics/export/<report_name>")
    @login_required
    def analytics_export(report_name: str):
        require_roles("admin", "doctor", "clerk", "researcher")
        exports = {
            "daily": ("SELECT * FROM v_daily_case_report ORDER BY case_date DESC, case_category", "daily_case_report.csv"),
            "monthly": ("SELECT * FROM v_monthly_statistics ORDER BY case_month DESC, case_category, case_type", "monthly_statistics.csv"),
            "pending": ("SELECT * FROM v_pending_reports ORDER BY due_date", "pending_reports.csv"),
        }
        if report_name not in exports:
            abort(404)
        sql, filename = exports[report_name]
        rows = get_db().execute(sql).fetchall()
        return csv_response(rows, filename)

    @app.route("/search")
    @login_required
    def global_search():
        require_roles("admin", "doctor", "clerk", "lab", "researcher")
        q = request.args.get("q", "").strip()
        results = []
        if q:
            like = f"%{q}%"
            db = get_db()
            results.extend(
                {
                    "type": "Patient",
                    "title": f"{row['patient_no']} - {row['full_name']}",
                    "subtitle": row["contact_no"] or row["gender"],
                    "url": url_for("module_list", module_key="patients", q=row["patient_no"]),
                }
                for row in db.execute(
                    "SELECT * FROM patients WHERE patient_no LIKE ? OR full_name LIKE ? OR nic LIKE ? LIMIT 10",
                    (like, like, like),
                ).fetchall()
            )
            results.extend(
                {
                    "type": "Case",
                    "title": f"{row['case_no']} - {row['case_type']}",
                    "subtitle": f"{row['patient_name']} / {row['status']}",
                    "url": url_for("case_detail", case_id=row["id"]),
                }
                for row in db.execute(
                    """
                    SELECT * FROM v_case_directory
                    WHERE case_no LIKE ? OR patient_name LIKE ? OR case_type LIKE ? OR police_station LIKE ?
                    LIMIT 10
                    """,
                    (like, like, like, like),
                ).fetchall()
            )
            results.extend(
                {
                    "type": "Evidence",
                    "title": row["evidence_code"],
                    "subtitle": f"{row['case_no']} / {row['evidence_type']} / {row['lab_status']}",
                    "url": url_for("evidence_detail", evidence_id=row["id"]),
                }
                for row in db.execute(
                    """
                    SELECT e.*, c.case_no
                    FROM evidence e
                    JOIN forensic_cases c ON c.id = e.case_id
                    WHERE e.evidence_code LIKE ? OR c.case_no LIKE ? OR e.evidence_type LIKE ?
                    LIMIT 10
                    """,
                    (like, like, like),
                ).fetchall()
            )
            results.extend(
                {
                    "type": "Report",
                    "title": row["report_no"],
                    "subtitle": f"{row['case_no']} / {row['report_type']} / {row['status']}",
                    "url": url_for("report_print", report_id=row["id"]),
                }
                for row in db.execute(
                    """
                    SELECT r.*, c.case_no
                    FROM court_reports r
                    JOIN forensic_cases c ON c.id = r.case_id
                    WHERE r.report_no LIKE ? OR c.case_no LIKE ? OR r.report_type LIKE ?
                    LIMIT 10
                    """,
                    (like, like, like),
                ).fetchall()
            )
        return render_template("search.html", q=q, results=results)

    @app.route("/users")
    @login_required
    def users_list():
        require_roles("admin")
        rows = get_db().execute(
            """
            SELECT u.id, u.username AS "Username", u.role AS "Role", COALESCE(s.full_name, '-') AS "Staff",
                   CASE u.is_active WHEN 1 THEN 'Yes' ELSE 'No' END AS "Active",
                   COALESCE(u.last_login, '-') AS "Last Login"
            FROM users u
            LEFT JOIN staff s ON s.id = u.staff_id
            ORDER BY u.username
            """
        ).fetchall()
        return render_template("users.html", rows=rows)

    @app.route("/users/new", methods=("GET", "POST"))
    @app.route("/users/<int:user_id>/edit", methods=("GET", "POST"))
    @login_required
    def user_form(user_id: int | None = None):
        require_roles("admin")
        db = get_db()
        user = None
        if user_id:
            user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            if not user:
                abort(404)
        values = dict(user) if user else {"is_active": 1}
        if request.method == "POST":
            values = {
                "staff_id": request.form.get("staff_id") or None,
                "username": request.form.get("username", "").strip(),
                "role": request.form.get("role", ""),
                "is_active": 1 if request.form.get("is_active") else 0,
            }
            password = request.form.get("password", "")
            errors = []
            if not values["username"]:
                errors.append("Username is required.")
            if values["role"] not in CHOICES["user_role"]:
                errors.append("A valid role is required.")
            if not user_id and not password:
                errors.append("Password is required for a new user.")
            if errors:
                for error in errors:
                    flash(error, "danger")
            else:
                if user_id:
                    if password:
                        values["password_hash"] = generate_password_hash(password)
                    update_record("users", user_id, values)
                    log_audit("update", "users", user_id, f"Updated user {values['username']}")
                    flash("User updated.", "success")
                else:
                    values["password_hash"] = generate_password_hash(password)
                    user_id = insert_record("users", values)
                    log_audit("create", "users", user_id, f"Created user {values['username']}")
                    flash("User created.", "success")
                return redirect(url_for("users_list"))
        fields = [
            {"name": "staff_id", "label": "Linked Staff", "type": "select", "source": "staff"},
            {"name": "username", "label": "Username", "required": True},
            {"name": "password", "label": "Password", "type": "password"},
            {"name": "role", "label": "Role", "type": "select", "choices": "user_role", "required": True},
            {"name": "is_active", "label": "Active", "type": "checkbox"},
        ]
        return render_template(
            "form.html",
            title="Edit User" if user_id else "New User",
            fields=prepare_fields(fields),
            values=values,
            action_url=request.path,
            cancel_url=url_for("users_list"),
        )

    @app.route("/users/<int:user_id>/delete", methods=("POST",))
    @login_required
    def user_delete(user_id: int):
        require_roles("admin")
        if user_id == g.user["id"]:
            flash("You cannot delete your own signed-in user.", "danger")
            return redirect(url_for("users_list"))
        db = get_db()
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        log_audit("delete", "users", user_id, "Deleted user")
        flash("User deleted.", "success")
        return redirect(url_for("users_list"))

    @app.route("/backup", methods=("GET", "POST"))
    @login_required
    def backup():
        require_roles("admin")
        backup_dir = Path(app.config["BACKUP_FOLDER"])
        backup_dir.mkdir(parents=True, exist_ok=True)
        if request.method == "POST":
            action = request.form.get("action")
            if action == "create":
                created = create_backup_file()
                log_audit("backup", "database", None, f"Created backup {created.name}")
                flash(f"Backup created: {created.name}", "success")
            elif action == "restore":
                filename = request.form.get("filename", "")
                restored = restore_backup_file(filename)
                log_audit("restore", "database", None, f"Restored backup {restored.name}")
                flash(f"Database restored from {restored.name}.", "success")
            return redirect(url_for("backup"))
        patterns = ("*.sql", "*.db") if app.config["DB_ENGINE"] == "mysql" else ("*.db",)
        backup_paths = []
        for pattern in patterns:
            backup_paths.extend(backup_dir.glob(pattern))
        backups = [
            {
                "name": path.name,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "size_kb": round(path.stat().st_size / 1024, 1),
            }
            for path in sorted(backup_paths, key=lambda p: p.stat().st_mtime, reverse=True)
        ]
        return render_template("backup.html", backups=backups)

    @app.route("/backup/download/<path:filename>")
    @login_required
    def backup_download(filename: str):
        require_roles("admin")
        backup_path = safe_backup_path(filename)
        return send_file(backup_path, as_attachment=True)

    @app.route("/notifications/<int:notification_id>/dismiss", methods=("POST",))
    @login_required
    def dismiss_notification(notification_id: int):
        require_roles("admin", "doctor", "clerk")
        db = get_db()
        db.execute("UPDATE notifications SET status = 'Dismissed' WHERE id = ?", (notification_id,))
        db.commit()
        log_audit("dismiss", "notifications", notification_id, "Dismissed notification")
        flash("Notification dismissed.", "success")
        return redirect(url_for("dashboard"))

    @app.cli.command("init-db")
    def init_db_command():
        init_db()
        print("Initialized the forensic database.")

    if app.config["DB_ENGINE"] == "sqlite":
        with app.app_context():
            init_db()

    return app


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        if current_app.config["DB_ENGINE"] == "mysql":
            g.db = connect_mysql()
        else:
            db_path = Path(current_app.config["DATABASE"])
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db = sqlite3.connect(db_path)
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys = ON")
            g.db = db
    return g.db


class MySQLRow(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class MySQLCursor:
    def __init__(self, cursor):
        self.cursor = cursor
        self.lastrowid = cursor.lastrowid

    def fetchone(self):
        row = self.cursor.fetchone()
        return MySQLRow(row) if row is not None else None

    def fetchall(self):
        return [MySQLRow(row) for row in self.cursor.fetchall()]


class MySQLDatabase:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, sql: str, params: tuple = ()):
        cursor = self.connection.cursor()
        converted = mysql_sql(sql)
        if params:
            cursor.execute(converted, params)
        else:
            cursor.execute(converted)
        return MySQLCursor(cursor)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


def mysql_sql(sql: str) -> str:
    return sql.replace("?", "%s")


def connect_mysql() -> MySQLDatabase:
    os.environ.pop("SSLKEYLOGFILE", None)
    try:
        import pymysql
        from pymysql.cursors import DictCursor
    except ImportError as exc:
        raise RuntimeError(
            "PyMySQL is required for MySQL mode. Run: python -m pip install -r codes\\Backend\\requirements.txt"
        ) from exc

    connection = pymysql.connect(
        host=current_app.config["MYSQL_HOST"],
        port=current_app.config["MYSQL_PORT"],
        user=current_app.config["MYSQL_USER"],
        password=current_app.config["MYSQL_PASSWORD"],
        database=current_app.config["MYSQL_DATABASE"],
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )
    return MySQLDatabase(connection)


def current_app_database() -> str:
    return current_app.config["DATABASE"]


def init_db() -> None:
    if current_app.config["DB_ENGINE"] == "mysql":
        return
    db_path = Path(current_app_database())
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    schema_path = DATA_DIR / "sqlite_schema.sql"
    seed_path = DATA_DIR / "sqlite_seed.sql"
    if not schema_path.exists():
        schema_path = PROJECT_ROOT / "schema.sql"
    if not seed_path.exists():
        seed_path = PROJECT_ROOT / "seed.sql"
    db.executescript(schema_path.read_text(encoding="utf-8"))
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        db.executescript(seed_path.read_text(encoding="utf-8"))
    db.commit()


def csrf_token() -> str:
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.get("user") is None:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def has_role(*roles: str) -> bool:
    user = g.get("user")
    if not user:
        return False
    if user["role"] == "admin":
        return True
    return user["role"] in roles


def require_roles(*roles: str) -> None:
    if not has_role(*roles):
        abort(403)


def get_module(module_key: str) -> dict:
    config = MODULES.get(module_key)
    if not config:
        abort(404)
    return config


def visible_nav_groups():
    groups = []
    for group_name, keys in NAV_GROUPS:
        items = []
        for key in keys:
            config = MODULES[key]
            if has_role(*config["read_roles"]):
                items.append({"key": key, "label": config["label"], "url": url_for("module_list", module_key=key)})
        if items:
            groups.append((group_name, items))
    return groups


def prepare_fields(fields: list[dict]) -> list[dict]:
    prepared = []
    for field in fields:
        item = dict(field)
        if item.get("type") == "select":
            if item.get("choices"):
                item["options"] = [(choice, choice) for choice in CHOICES[item["choices"]]]
            elif item.get("source"):
                item["options"] = source_options(item["source"])
            if not item.get("required"):
                item["options"] = [("", "Unassigned")] + item["options"]
        prepared.append(item)
    return prepared


def source_options(source: str) -> list[tuple[str, str]]:
    db = get_db()
    queries = {
        "patients": "SELECT id, patient_no || ' - ' || full_name AS label FROM patients ORDER BY patient_no",
        "cases": "SELECT id, case_no || ' - ' || case_type AS label FROM forensic_cases ORDER BY case_no",
        "clinical_cases": """
            SELECT id, case_no || ' - ' || case_type AS label
            FROM forensic_cases
            WHERE case_category = 'Clinical'
            ORDER BY case_no
        """,
        "autopsy_cases": """
            SELECT id, case_no || ' - ' || case_type AS label
            FROM forensic_cases
            WHERE case_category = 'Autopsy'
            ORDER BY case_no
        """,
        "doctors": """
            SELECT id, staff_code || ' - ' || full_name AS label
            FROM staff
            WHERE active = 1 AND staff_role IN ('Judicial Medical Officer', 'Doctor')
            ORDER BY full_name
        """,
        "staff": "SELECT id, staff_code || ' - ' || full_name AS label FROM staff WHERE active = 1 ORDER BY full_name",
        "evidence": "SELECT id, evidence_code || ' - ' || evidence_type AS label FROM evidence ORDER BY evidence_code",
    }
    if source not in queries:
        return []
    return [(str(row["id"]), row["label"]) for row in db.execute(queries[source]).fetchall()]


def default_values(fields: list[dict]) -> dict:
    values = {}
    for field in fields:
        if field.get("type") == "checkbox":
            values[field["name"]] = 1 if field.get("name") == "active" else 0
        elif field.get("name") == "status" and "choices" in field:
            values[field["name"]] = CHOICES[field["choices"]][0]
        elif field.get("choices"):
            values[field["name"]] = CHOICES[field["choices"]][0] if field.get("required") else ""
        else:
            values[field["name"]] = ""
    return values


def collect_form_values(fields: list[dict]) -> dict:
    values = {}
    for field in fields:
        name = field["name"]
        field_type = field.get("type", "text")
        if field_type == "checkbox":
            values[name] = 1 if request.form.get(name) else 0
        else:
            value = request.form.get(name, "").strip()
            if field_type == "datetime-local":
                value = normalize_datetime(value)
            values[name] = value if value != "" else None
    return values


def validate_values(fields: list[dict], values: dict) -> list[str]:
    errors = []
    for field in fields:
        if field.get("required") and values.get(field["name"]) in (None, ""):
            errors.append(f"{field['label']} is required.")
    return errors


def normalize_datetime(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace("T", " ")


def insert_record(table: str, values: dict) -> int:
    columns = list(values.keys())
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    db = get_db()
    cursor = db.execute(sql, tuple(values[column] for column in columns))
    db.commit()
    return cursor.lastrowid


def update_record(table: str, item_id: int, values: dict) -> None:
    columns = list(values.keys())
    assignments = ", ".join([f"{column} = ?" for column in columns])
    db = get_db()
    db.execute(f"UPDATE {table} SET {assignments} WHERE id = ?", tuple(values[column] for column in columns) + (item_id,))
    db.commit()


def update_barcode_value(evidence_id: int) -> None:
    db = get_db()
    row = db.execute(
        """
        SELECT e.evidence_code, c.case_no
        FROM evidence e
        JOIN forensic_cases c ON c.id = e.case_id
        WHERE e.id = ?
        """,
        (evidence_id,),
    ).fetchone()
    if row:
        db.execute("UPDATE evidence SET barcode_value = ? WHERE id = ?", (f"{row['evidence_code']}|{row['case_no']}", evidence_id))
        db.commit()


def redirect_after_save(module_key: str, item_id: int):
    if module_key == "cases":
        return redirect(url_for("case_detail", case_id=item_id))
    if module_key == "evidence":
        return redirect(url_for("evidence_detail", evidence_id=item_id))
    if module_key == "reports":
        return redirect(url_for("report_print", report_id=item_id))
    return redirect(url_for("module_list", module_key=module_key))


def log_audit(action: str, entity: str, entity_id: int | None, details: str) -> None:
    user = g.get("user")
    actor_id = user["id"] if user else None
    db = get_db()
    db.execute(
        """
        INSERT INTO audit_logs (actor_user_id, action, entity, entity_id, details)
        VALUES (?, ?, ?, ?, ?)
        """,
        (actor_id, action, entity, entity_id, details),
    )
    db.commit()


def barcode_bars(value: str) -> list[int]:
    numbers = []
    for char in value:
        numbers.append((ord(char) % 4) + 1)
        numbers.append(((ord(char) // 3) % 3) + 1)
    return numbers[:80]


def csv_response(rows: list[sqlite3.Row], filename: str):
    output = io.StringIO()
    writer = csv.writer(output)
    if rows:
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow([row[key] for key in row.keys()])
    else:
        writer.writerow(["No data"])
    buffer = io.BytesIO(output.getvalue().encode("utf-8"))
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="text/csv")


def create_backup_file() -> Path:
    if current_app.config["DB_ENGINE"] == "mysql":
        return create_mysql_backup_file()
    db_path = Path(current_app.config["DATABASE"])
    backup_dir = Path(current_app.config["BACKUP_FOLDER"])
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"forensic_{stamp}.db"
    db = g.pop("db", None)
    if db is not None:
        db.close()
    shutil.copy2(db_path, backup_path)
    return backup_path


def safe_backup_path(filename: str) -> Path:
    backup_dir = Path(current_app.config["BACKUP_FOLDER"]).resolve()
    target = (backup_dir / filename).resolve()
    allowed_suffixes = {".sql", ".db"} if current_app.config["DB_ENGINE"] == "mysql" else {".db"}
    if backup_dir not in target.parents or target.suffix.lower() not in allowed_suffixes or not target.exists():
        abort(404)
    return target


def restore_backup_file(filename: str) -> Path:
    source = safe_backup_path(filename)
    if current_app.config["DB_ENGINE"] == "mysql":
        restore_mysql_backup_file(source)
        return source
    db_path = Path(current_app.config["DATABASE"])
    db = g.pop("db", None)
    if db is not None:
        db.close()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safety_copy = Path(current_app.config["BACKUP_FOLDER"]) / f"before_restore_{timestamp}.db"
    if db_path.exists():
        shutil.copy2(db_path, safety_copy)
    shutil.copy2(source, db_path)
    return source


MYSQL_TABLES = [
    "staff",
    "users",
    "patients",
    "forensic_cases",
    "clinical_examinations",
    "postmortems",
    "documents",
    "evidence",
    "chain_of_custody",
    "lab_tests",
    "court_reports",
    "notifications",
    "audit_logs",
]

MYSQL_VIEWS = [
    "v_case_directory",
    "v_pending_reports",
    "v_daily_case_report",
    "v_monthly_statistics",
]


def create_mysql_backup_file() -> Path:
    backup_dir = Path(current_app.config["BACKUP_FOLDER"])
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"forensic_mysql_{stamp}.sql"
    db = get_db()
    lines = [
        "SET FOREIGN_KEY_CHECKS = 0;",
        f"USE `{current_app.config['MYSQL_DATABASE']}`;",
        "",
    ]
    for view in MYSQL_VIEWS:
        lines.append(f"DROP VIEW IF EXISTS `{view}`;")
    for table in reversed(MYSQL_TABLES):
        lines.append(f"DROP TABLE IF EXISTS `{table}`;")
    lines.append("")
    for table in MYSQL_TABLES:
        create_row = db.execute(f"SHOW CREATE TABLE `{table}`").fetchone()
        create_sql = list(create_row.values())[1]
        lines.append(f"{create_sql};")
        rows = db.execute(f"SELECT * FROM `{table}`").fetchall()
        if rows:
            columns = list(rows[0].keys())
            column_sql = ", ".join(f"`{column}`" for column in columns)
            for row in rows:
                values = ", ".join(mysql_literal(row[column]) for column in columns)
                lines.append(f"INSERT INTO `{table}` ({column_sql}) VALUES ({values});")
        lines.append("")
    for view in MYSQL_VIEWS:
        create_row = db.execute(f"SHOW CREATE VIEW `{view}`").fetchone()
        create_sql = list(create_row.values())[1]
        lines.append(f"{create_sql};")
        lines.append("")
    lines.append("SET FOREIGN_KEY_CHECKS = 1;")
    backup_path.write_text("\n".join(lines), encoding="utf-8")
    return backup_path


def mysql_literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{text}'"


def restore_mysql_backup_file(path: Path) -> None:
    script = path.read_text(encoding="utf-8")
    db = get_db()
    for statement in split_sql_statements(script):
        if statement.strip():
            db.execute(statement)
    db.commit()


def split_sql_statements(script: str) -> list[str]:
    statements = []
    current = []
    in_string = False
    escape = False
    quote = ""
    for char in script:
        current.append(char)
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                in_string = False
        elif char in ("'", '"'):
            in_string = True
            quote = char
        elif char == ";":
            statements.append("".join(current[:-1]).strip())
            current = []
    tail = "".join(current).strip()
    if tail:
        statements.append(tail)
    return statements


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
