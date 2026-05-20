PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_code TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    staff_role TEXT NOT NULL CHECK (staff_role IN (
        'Judicial Medical Officer',
        'Doctor',
        'Laboratory Staff',
        'Clerical Officer',
        'Administrator'
    )),
    specialization TEXT,
    contact_no TEXT,
    email TEXT,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER REFERENCES staff(id) ON DELETE SET NULL,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'doctor', 'clerk', 'lab', 'researcher')),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_login TEXT,
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_no TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    nic TEXT,
    dob TEXT,
    age INTEGER CHECK (age IS NULL OR age >= 0),
    gender TEXT NOT NULL CHECK (gender IN ('Female', 'Male', 'Other', 'Unknown')),
    address TEXT,
    contact_no TEXT,
    guardian_name TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS forensic_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_no TEXT NOT NULL UNIQUE,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    case_category TEXT NOT NULL CHECK (case_category IN ('Clinical', 'Autopsy')),
    case_type TEXT NOT NULL,
    referral_source TEXT,
    authorization_type TEXT NOT NULL CHECK (authorization_type IN (
        'MLEF',
        'Request Letter',
        'Court Order',
        'Inquest Order',
        'Other'
    )),
    authorization_ref TEXT,
    incident_date TEXT,
    incident_location TEXT,
    police_station TEXT,
    assigned_doctor_id INTEGER REFERENCES staff(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN (
        'Open',
        'In Review',
        'Report Pending',
        'Closed',
        'Archived'
    )),
    summary TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (assigned_doctor_id) REFERENCES staff(id)
);

CREATE TABLE IF NOT EXISTS clinical_examinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL UNIQUE REFERENCES forensic_cases(id) ON DELETE CASCADE,
    mlef_no TEXT NOT NULL UNIQUE,
    examined_at TEXT,
    history TEXT,
    findings TEXT,
    injuries TEXT,
    investigation_findings TEXT,
    referral_notes TEXT,
    review_notes TEXT,
    photos_path TEXT,
    issued_police_copy INTEGER NOT NULL DEFAULT 0 CHECK (issued_police_copy IN (0, 1)),
    mlr_status TEXT NOT NULL DEFAULT 'Pending' CHECK (mlr_status IN ('Pending', 'Drafted', 'Issued')),
    next_court_date TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (case_id) REFERENCES forensic_cases(id)
);

CREATE TABLE IF NOT EXISTS postmortems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL UNIQUE REFERENCES forensic_cases(id) ON DELETE CASCADE,
    pmr_no TEXT NOT NULL UNIQUE,
    death_type TEXT NOT NULL CHECK (death_type IN (
        'Natural',
        'Accidental',
        'Suicidal',
        'Homicidal',
        'Undetermined'
    )),
    inquest_order_no TEXT,
    autopsy_date TEXT,
    pre_autopsy_info TEXT,
    external_findings TEXT,
    internal_findings TEXT,
    cause_of_death TEXT,
    cod_status TEXT NOT NULL DEFAULT 'Pending' CHECK (cod_status IN ('Pending', 'Drafted', 'Issued')),
    histology_status TEXT NOT NULL DEFAULT 'Not Required' CHECK (histology_status IN (
        'Not Required',
        'Pending',
        'Received'
    )),
    photos_path TEXT,
    audio_transcript_ref TEXT,
    next_court_date TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (case_id) REFERENCES forensic_cases(id)
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES forensic_cases(id) ON DELETE CASCADE,
    document_type TEXT NOT NULL CHECK (document_type IN (
        'MLEF Doctor Copy',
        'Photo',
        'Investigation',
        'Referral Report',
        'Summons',
        'Issued Report Copy',
        'Certificate Receipt',
        'Court Order',
        'Inquest Order',
        'PMR Scan',
        'COD Form',
        'Other'
    )),
    reference_no TEXT,
    storage_ref TEXT,
    received_at TEXT,
    issued_to TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (case_id) REFERENCES forensic_cases(id)
);

CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evidence_code TEXT NOT NULL UNIQUE,
    case_id INTEGER NOT NULL REFERENCES forensic_cases(id) ON DELETE CASCADE,
    evidence_type TEXT NOT NULL,
    description TEXT,
    collected_at TEXT,
    collected_by_staff_id INTEGER REFERENCES staff(id) ON DELETE SET NULL,
    storage_location TEXT,
    lab_status TEXT NOT NULL DEFAULT 'Not Sent' CHECK (lab_status IN (
        'Not Sent',
        'Pending',
        'Completed',
        'Returned'
    )),
    barcode_value TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (case_id) REFERENCES forensic_cases(id),
    FOREIGN KEY (collected_by_staff_id) REFERENCES staff(id)
);

CREATE TABLE IF NOT EXISTS chain_of_custody (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evidence_id INTEGER NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (action IN ('Collected', 'Transferred', 'Stored', 'Tested', 'Returned', 'Disposed')),
    from_holder TEXT,
    to_holder TEXT NOT NULL,
    handled_by_staff_id INTEGER REFERENCES staff(id) ON DELETE SET NULL,
    action_at TEXT NOT NULL,
    location TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (evidence_id) REFERENCES evidence(id),
    FOREIGN KEY (handled_by_staff_id) REFERENCES staff(id)
);

CREATE TABLE IF NOT EXISTS lab_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_code TEXT NOT NULL UNIQUE,
    evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
    case_id INTEGER NOT NULL REFERENCES forensic_cases(id) ON DELETE CASCADE,
    test_type TEXT NOT NULL,
    requested_at TEXT,
    requested_by_staff_id INTEGER REFERENCES staff(id) ON DELETE SET NULL,
    result TEXT,
    status TEXT NOT NULL DEFAULT 'Requested' CHECK (status IN (
        'Requested',
        'In Progress',
        'Completed',
        'Cancelled'
    )),
    report_ref TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (evidence_id) REFERENCES evidence(id),
    FOREIGN KEY (case_id) REFERENCES forensic_cases(id),
    FOREIGN KEY (requested_by_staff_id) REFERENCES staff(id)
);

CREATE TABLE IF NOT EXISTS court_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_no TEXT NOT NULL UNIQUE,
    case_id INTEGER NOT NULL REFERENCES forensic_cases(id) ON DELETE CASCADE,
    report_type TEXT NOT NULL CHECK (report_type IN (
        'MLR',
        'PMR',
        'COD',
        'Court Submission',
        'Research Summary',
        'Other'
    )),
    requested_by TEXT,
    requested_at TEXT,
    due_date TEXT,
    submission_date TEXT,
    status TEXT NOT NULL DEFAULT 'Requested' CHECK (status IN (
        'Requested',
        'Drafting',
        'Submitted',
        'Closed'
    )),
    prepared_by_staff_id INTEGER REFERENCES staff(id) ON DELETE SET NULL,
    summary TEXT,
    digital_signature TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (case_id) REFERENCES forensic_cases(id),
    FOREIGN KEY (prepared_by_staff_id) REFERENCES staff(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    case_id INTEGER REFERENCES forensic_cases(id) ON DELETE CASCADE,
    report_id INTEGER REFERENCES court_reports(id) ON DELETE CASCADE,
    due_date TEXT,
    status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Dismissed')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (case_id) REFERENCES forensic_cases(id),
    FOREIGN KEY (report_id) REFERENCES court_reports(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    entity_id INTEGER,
    details TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (actor_user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_cases_patient ON forensic_cases(patient_id);
CREATE INDEX IF NOT EXISTS idx_cases_category_status ON forensic_cases(case_category, status);
CREATE INDEX IF NOT EXISTS idx_clinical_mlef ON clinical_examinations(mlef_no);
CREATE INDEX IF NOT EXISTS idx_postmortem_pmr ON postmortems(pmr_no);
CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence(case_id);
CREATE INDEX IF NOT EXISTS idx_reports_case_status ON court_reports(case_id, status);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);

CREATE TRIGGER IF NOT EXISTS trg_staff_updated_at
AFTER UPDATE ON staff
FOR EACH ROW
BEGIN
    UPDATE staff SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_patients_updated_at
AFTER UPDATE ON patients
FOR EACH ROW
BEGIN
    UPDATE patients SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_cases_updated_at
AFTER UPDATE ON forensic_cases
FOR EACH ROW
BEGIN
    UPDATE forensic_cases SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_clinical_updated_at
AFTER UPDATE ON clinical_examinations
FOR EACH ROW
BEGIN
    UPDATE clinical_examinations SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_postmortem_updated_at
AFTER UPDATE ON postmortems
FOR EACH ROW
BEGIN
    UPDATE postmortems SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_evidence_updated_at
AFTER UPDATE ON evidence
FOR EACH ROW
BEGIN
    UPDATE evidence SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_lab_tests_updated_at
AFTER UPDATE ON lab_tests
FOR EACH ROW
BEGIN
    UPDATE lab_tests SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_reports_updated_at
AFTER UPDATE ON court_reports
FOR EACH ROW
BEGIN
    UPDATE court_reports SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE VIEW IF NOT EXISTS v_case_directory AS
SELECT
    c.id,
    c.case_no,
    c.case_category,
    c.case_type,
    c.status,
    c.incident_date,
    p.patient_no,
    p.full_name AS patient_name,
    p.gender,
    s.full_name AS assigned_doctor,
    c.authorization_type,
    c.authorization_ref,
    c.police_station
FROM forensic_cases c
JOIN patients p ON p.id = c.patient_id
LEFT JOIN staff s ON s.id = c.assigned_doctor_id;

CREATE VIEW IF NOT EXISTS v_pending_reports AS
SELECT
    r.id,
    r.report_no,
    r.report_type,
    r.status,
    r.due_date,
    c.case_no,
    p.full_name AS patient_name,
    s.full_name AS prepared_by
FROM court_reports r
JOIN forensic_cases c ON c.id = r.case_id
JOIN patients p ON p.id = c.patient_id
LEFT JOIN staff s ON s.id = r.prepared_by_staff_id
WHERE r.status IN ('Requested', 'Drafting');

CREATE VIEW IF NOT EXISTS v_daily_case_report AS
SELECT
    date(created_at) AS case_date,
    case_category,
    COUNT(*) AS total_cases
FROM forensic_cases
GROUP BY date(created_at), case_category;

CREATE VIEW IF NOT EXISTS v_monthly_statistics AS
SELECT
    strftime('%Y-%m', created_at) AS case_month,
    case_category,
    case_type,
    COUNT(*) AS total_cases
FROM forensic_cases
GROUP BY strftime('%Y-%m', created_at), case_category, case_type;
