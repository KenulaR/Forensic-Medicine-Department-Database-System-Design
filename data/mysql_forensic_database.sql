-- Forensic Medicine Department Database System
-- MySQL 8+ setup script.
-- Copy-paste this whole file into MySQL Workbench, MySQL Shell, or the mysql CLI.

DROP DATABASE IF EXISTS forensic_medicine_db;
CREATE DATABASE forensic_medicine_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE forensic_medicine_db;

CREATE USER IF NOT EXISTS 'forensic_user'@'localhost' IDENTIFIED BY 'forensic123';
CREATE USER IF NOT EXISTS 'forensic_user'@'127.0.0.1' IDENTIFIED BY 'forensic123';
GRANT ALL PRIVILEGES ON forensic_medicine_db.* TO 'forensic_user'@'localhost';
GRANT ALL PRIVILEGES ON forensic_medicine_db.* TO 'forensic_user'@'127.0.0.1';
FLUSH PRIVILEGES;

CREATE TABLE staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_code VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(160) NOT NULL,
    staff_role ENUM('Judicial Medical Officer', 'Doctor', 'Laboratory Staff', 'Clerical Officer', 'Administrator') NOT NULL,
    specialization VARCHAR(160),
    contact_no VARCHAR(40),
    email VARCHAR(160),
    active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NULL,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'doctor', 'clerk', 'lab', 'researcher') NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    CONSTRAINT fk_users_staff FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_no VARCHAR(40) NOT NULL UNIQUE,
    full_name VARCHAR(180) NOT NULL,
    nic VARCHAR(40),
    dob DATE,
    age INT,
    gender ENUM('Female', 'Male', 'Other', 'Unknown') NOT NULL,
    address TEXT,
    contact_no VARCHAR(40),
    guardian_name VARCHAR(180),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_patients_age CHECK (age IS NULL OR age >= 0)
) ENGINE=InnoDB;

CREATE TABLE forensic_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_no VARCHAR(40) NOT NULL UNIQUE,
    patient_id INT NOT NULL,
    case_category ENUM('Clinical', 'Autopsy') NOT NULL,
    case_type VARCHAR(80) NOT NULL,
    referral_source VARCHAR(180),
    authorization_type ENUM('MLEF', 'Request Letter', 'Court Order', 'Inquest Order', 'Other') NOT NULL,
    authorization_ref VARCHAR(120),
    incident_date DATE,
    incident_location VARCHAR(180),
    police_station VARCHAR(180),
    assigned_doctor_id INT NULL,
    status ENUM('Open', 'In Review', 'Report Pending', 'Closed', 'Archived') NOT NULL DEFAULT 'Open',
    summary TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_cases_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    CONSTRAINT fk_cases_doctor FOREIGN KEY (assigned_doctor_id) REFERENCES staff(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE clinical_examinations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL UNIQUE,
    mlef_no VARCHAR(60) NOT NULL UNIQUE,
    examined_at DATETIME,
    history TEXT,
    findings TEXT,
    injuries TEXT,
    investigation_findings TEXT,
    referral_notes TEXT,
    review_notes TEXT,
    photos_path VARCHAR(255),
    issued_police_copy TINYINT(1) NOT NULL DEFAULT 0,
    mlr_status ENUM('Pending', 'Drafted', 'Issued') NOT NULL DEFAULT 'Pending',
    next_court_date DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_clinical_case FOREIGN KEY (case_id) REFERENCES forensic_cases(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE postmortems (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL UNIQUE,
    pmr_no VARCHAR(60) NOT NULL UNIQUE,
    death_type ENUM('Natural', 'Accidental', 'Suicidal', 'Homicidal', 'Undetermined') NOT NULL,
    inquest_order_no VARCHAR(120),
    autopsy_date DATETIME,
    pre_autopsy_info TEXT,
    external_findings TEXT,
    internal_findings TEXT,
    cause_of_death TEXT,
    cod_status ENUM('Pending', 'Drafted', 'Issued') NOT NULL DEFAULT 'Pending',
    histology_status ENUM('Not Required', 'Pending', 'Received') NOT NULL DEFAULT 'Not Required',
    photos_path VARCHAR(255),
    audio_transcript_ref VARCHAR(255),
    next_court_date DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_postmortem_case FOREIGN KEY (case_id) REFERENCES forensic_cases(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    document_type ENUM('MLEF Doctor Copy', 'Photo', 'Investigation', 'Referral Report', 'Summons', 'Issued Report Copy', 'Certificate Receipt', 'Court Order', 'Inquest Order', 'PMR Scan', 'COD Form', 'Other') NOT NULL,
    reference_no VARCHAR(120),
    storage_ref VARCHAR(255),
    received_at DATE,
    issued_to VARCHAR(180),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_case FOREIGN KEY (case_id) REFERENCES forensic_cases(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE evidence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evidence_code VARCHAR(60) NOT NULL UNIQUE,
    case_id INT NOT NULL,
    evidence_type VARCHAR(100) NOT NULL,
    description TEXT,
    collected_at DATETIME,
    collected_by_staff_id INT NULL,
    storage_location VARCHAR(180),
    lab_status ENUM('Not Sent', 'Pending', 'Completed', 'Returned') NOT NULL DEFAULT 'Not Sent',
    barcode_value VARCHAR(180),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_evidence_case FOREIGN KEY (case_id) REFERENCES forensic_cases(id) ON DELETE CASCADE,
    CONSTRAINT fk_evidence_collector FOREIGN KEY (collected_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE chain_of_custody (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evidence_id INT NOT NULL,
    action ENUM('Collected', 'Transferred', 'Stored', 'Tested', 'Returned', 'Disposed') NOT NULL,
    from_holder VARCHAR(180),
    to_holder VARCHAR(180) NOT NULL,
    handled_by_staff_id INT NULL,
    action_at DATETIME NOT NULL,
    location VARCHAR(180),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_custody_evidence FOREIGN KEY (evidence_id) REFERENCES evidence(id) ON DELETE CASCADE,
    CONSTRAINT fk_custody_staff FOREIGN KEY (handled_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE lab_tests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_code VARCHAR(60) NOT NULL UNIQUE,
    evidence_id INT NULL,
    case_id INT NOT NULL,
    test_type VARCHAR(100) NOT NULL,
    requested_at DATETIME,
    requested_by_staff_id INT NULL,
    result TEXT,
    status ENUM('Requested', 'In Progress', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Requested',
    report_ref VARCHAR(180),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_lab_evidence FOREIGN KEY (evidence_id) REFERENCES evidence(id) ON DELETE SET NULL,
    CONSTRAINT fk_lab_case FOREIGN KEY (case_id) REFERENCES forensic_cases(id) ON DELETE CASCADE,
    CONSTRAINT fk_lab_staff FOREIGN KEY (requested_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE court_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_no VARCHAR(60) NOT NULL UNIQUE,
    case_id INT NOT NULL,
    report_type ENUM('MLR', 'PMR', 'COD', 'Court Submission', 'Research Summary', 'Other') NOT NULL,
    requested_by VARCHAR(180),
    requested_at DATE,
    due_date DATE,
    submission_date DATE,
    status ENUM('Requested', 'Drafting', 'Submitted', 'Closed') NOT NULL DEFAULT 'Requested',
    prepared_by_staff_id INT NULL,
    summary TEXT,
    digital_signature VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_reports_case FOREIGN KEY (case_id) REFERENCES forensic_cases(id) ON DELETE CASCADE,
    CONSTRAINT fk_reports_staff FOREIGN KEY (prepared_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(180) NOT NULL,
    message TEXT NOT NULL,
    case_id INT NULL,
    report_id INT NULL,
    due_date DATE,
    status ENUM('Open', 'Dismissed') NOT NULL DEFAULT 'Open',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notifications_case FOREIGN KEY (case_id) REFERENCES forensic_cases(id) ON DELETE CASCADE,
    CONSTRAINT fk_notifications_report FOREIGN KEY (report_id) REFERENCES court_reports(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    actor_user_id INT NULL,
    action VARCHAR(80) NOT NULL,
    entity VARCHAR(80) NOT NULL,
    entity_id INT NULL,
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX idx_cases_patient ON forensic_cases(patient_id);
CREATE INDEX idx_cases_category_status ON forensic_cases(case_category, status);
CREATE INDEX idx_clinical_mlef ON clinical_examinations(mlef_no);
CREATE INDEX idx_postmortem_pmr ON postmortems(pmr_no);
CREATE INDEX idx_evidence_case ON evidence(case_id);
CREATE INDEX idx_reports_case_status ON court_reports(case_id, status);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

CREATE VIEW v_case_directory AS
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

CREATE VIEW v_pending_reports AS
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

CREATE VIEW v_daily_case_report AS
SELECT
    DATE(created_at) AS case_date,
    case_category,
    COUNT(*) AS total_cases
FROM forensic_cases
GROUP BY DATE(created_at), case_category;

CREATE VIEW v_monthly_statistics AS
SELECT
    DATE_FORMAT(created_at, '%Y-%m') AS case_month,
    case_category,
    case_type,
    COUNT(*) AS total_cases
FROM forensic_cases
GROUP BY DATE_FORMAT(created_at, '%Y-%m'), case_category, case_type;

INSERT INTO staff (id, staff_code, full_name, staff_role, specialization, contact_no, email) VALUES
    (1, 'STF-001', 'Dr. A. Wijesinghe', 'Judicial Medical Officer', 'Clinical forensic medicine', '0711111111', 'jmo@example.local'),
    (2, 'STF-002', 'Dr. M. Fernando', 'Doctor', 'Forensic pathology', '0712222222', 'doctor@example.local'),
    (3, 'STF-003', 'N. Perera', 'Laboratory Staff', 'Toxicology', '0713333333', 'lab@example.local'),
    (4, 'STF-004', 'S. Jayawardena', 'Clerical Officer', 'Records and court dispatch', '0714444444', 'clerk@example.local'),
    (5, 'STF-005', 'System Administrator', 'Administrator', 'Database administration', '0715555555', 'admin@example.local');

INSERT INTO users (staff_id, username, password_hash, role) VALUES
    (5, 'admin', 'pbkdf2:sha256:1000000$gRKhjZJW0pkxWW2N$107a000d84d0b1bec0564709de636d539099e98e7b1e06db5d43934470004256', 'admin'),
    (1, 'doctor', 'pbkdf2:sha256:1000000$bJElMRTknGWqEnHz$db4018724ef51cf2d060f8420b9c802f8d5b848f44dd2630f86657fa1bee9521', 'doctor'),
    (4, 'clerk', 'pbkdf2:sha256:1000000$XMNXR0T7Sp5yNf3F$c2c3d5562c0d725acee450ff3fc18f658afe21f064abd56dc3549fce76b85f17', 'clerk'),
    (3, 'lab', 'pbkdf2:sha256:1000000$Oz8ne74bb89HLsV3$4c211943d6a14f54d395daeb5b00c2edfc220b3a65893ec3216125169a5c10cb', 'lab'),
    (NULL, 'researcher', 'pbkdf2:sha256:1000000$RtNql6kPn8VaLHPC$d1ab59936423d551c42d96b43dc59ae7646084647f773a7d7a4223fcae8980b7', 'researcher');

INSERT INTO patients (id, patient_no, full_name, nic, dob, age, gender, address, contact_no, guardian_name) VALUES
    (1, 'PAT-2026-001', 'Nadeeka Perera', '945670123V', '1994-03-14', 32, 'Female', 'No. 12, Kandy Road, Peradeniya', '0771001001', NULL),
    (2, 'PAT-2026-002', 'Kamal Silva', '852344567V', '1985-09-20', 40, 'Male', 'No. 45, Katugastota', '0771001002', NULL),
    (3, 'PAT-2026-003', 'Unidentified Male', NULL, NULL, 68, 'Unknown', 'Brought by hospital mortuary', NULL, NULL),
    (4, 'PAT-2026-004', 'Protected Child Record', NULL, '2014-02-10', 12, 'Female', 'Confidential', '0771001004', 'Mother recorded in sealed file');

INSERT INTO forensic_cases (
    id, case_no, patient_id, case_category, case_type, referral_source,
    authorization_type, authorization_ref, incident_date, incident_location,
    police_station, assigned_doctor_id, status, summary
) VALUES
    (1, 'CL-2026-001', 1, 'Clinical', 'Domestic abuse', 'Ward informed hospital police', 'MLEF', 'MLEF/KDY/2026/118', '2026-05-16', 'Peradeniya', 'Peradeniya Police', 1, 'Report Pending', 'Assault history with visible soft tissue injuries.'),
    (2, 'CL-2026-002', 2, 'Clinical', 'Detainee examination', 'Nearby police station', 'Request Letter', 'REQ/KDY/2026/209', '2026-05-18', 'Kandy', 'Kandy Police', 1, 'In Review', 'Detainee examination and toxicology request.'),
    (3, 'PM-2026-001', 3, 'Autopsy', 'Hospital death', 'Ward informed ISD and police', 'Inquest Order', 'INQ/KDY/2026/088', '2026-05-10', 'Teaching Hospital Kandy', 'Kandy Police', 2, 'Report Pending', 'Elderly male hospital death. PMR and COD pending final review.'),
    (4, 'PM-2026-002', 4, 'Autopsy', 'Outside death', 'Police ISD referral', 'Court Order', 'CRT/KDY/2026/044', '2026-05-13', 'Gampola', 'Gampola Police', 2, 'Open', 'High priority outside death with requested histology.');

INSERT INTO clinical_examinations (
    case_id, mlef_no, examined_at, history, findings, injuries,
    investigation_findings, referral_notes, review_notes, photos_path,
    issued_police_copy, mlr_status, next_court_date
) VALUES
    (1, 'MLEF-2026-001', '2026-05-16 14:30:00', 'Patient alleges assault by spouse.', 'Patient conscious, oriented, anxious.', 'Bruising over left forearm and right shoulder.', 'X-ray requested. No fracture reported.', 'Psychiatry referral requested.', 'Outpatient review in 7 days.', 'storage/clinical/CL-2026-001/photos', 1, 'Drafted', '2026-06-05'),
    (2, 'MLEF-2026-002', '2026-05-18 09:15:00', 'Detainee brought by police for examination.', 'No acute distress. Old scar noted.', 'No fresh external injuries.', 'Blood and urine toxicology sent.', NULL, 'Awaiting toxicology.', 'storage/clinical/CL-2026-002/photos', 0, 'Pending', '2026-05-28');

INSERT INTO postmortems (
    case_id, pmr_no, death_type, inquest_order_no, autopsy_date,
    pre_autopsy_info, external_findings, internal_findings, cause_of_death,
    cod_status, histology_status, photos_path, audio_transcript_ref, next_court_date
) VALUES
    (3, 'PMR-2026-001', 'Natural', 'INQ/KDY/2026/088', '2026-05-11 10:00:00', 'BHT reviewed. Family statement recorded.', 'No external injuries of medico-legal significance.', 'Severe coronary artery atherosclerosis.', 'Ischaemic heart disease', 'Drafted', 'Not Required', 'storage/autopsy/PM-2026-001/photos', 'storage/autopsy/PM-2026-001/audio-transcript.txt', '2026-06-12'),
    (4, 'PMR-2026-002', 'Undetermined', 'CRT/KDY/2026/044', '2026-05-14 11:30:00', 'Crime scene photographs and police statements received.', 'Multiple abrasions noted.', 'Internal examination pending histology correlation.', NULL, 'Pending', 'Pending', 'storage/autopsy/PM-2026-002/photos', NULL, '2026-05-30');

INSERT INTO documents (case_id, document_type, reference_no, storage_ref, received_at, issued_to, notes) VALUES
    (1, 'MLEF Doctor Copy', 'MLEF/KDY/2026/118', 'cabinet/clinical/2026/CL-2026-001', '2026-05-16', NULL, 'Doctor copy filed.'),
    (1, 'Issued Report Copy', 'MLR-2026-001', 'storage/reports/MLR-2026-001.pdf', '2026-05-19', 'Peradeniya Police', 'Draft copy under review.'),
    (2, 'Investigation', 'TOX-2026-014', 'storage/lab/TOX-2026-014.pdf', '2026-05-18', NULL, 'Toxicology pending.'),
    (3, 'PMR Scan', 'PMR-2026-001', 'cabinet/autopsy/2026/PM-2026-001', '2026-05-11', NULL, 'Scanned PMR stored.'),
    (3, 'COD Form', 'COD-2026-001', 'storage/cod/COD-2026-001.pdf', '2026-05-12', NULL, 'COD draft prepared.'),
    (4, 'Court Order', 'CRT/KDY/2026/044', 'cabinet/autopsy/2026/PM-2026-002/order', '2026-05-13', NULL, 'Court order attached.');

INSERT INTO evidence (
    id, evidence_code, case_id, evidence_type, description, collected_at,
    collected_by_staff_id, storage_location, lab_status, barcode_value
) VALUES
    (1, 'EVD-2026-001', 2, 'Blood sample', 'Blood sample for toxicology.', '2026-05-18 10:00:00', 3, 'Lab fridge A2', 'Pending', 'EVD-2026-001|CL-2026-002'),
    (2, 'EVD-2026-002', 2, 'Urine sample', 'Urine sample for toxicology.', '2026-05-18 10:05:00', 3, 'Lab fridge A2', 'Pending', 'EVD-2026-002|CL-2026-002'),
    (3, 'EVD-2026-003', 4, 'Histology tissue block', 'Tissue sample retained for histology.', '2026-05-14 12:20:00', 3, 'Histology shelf H1', 'Pending', 'EVD-2026-003|PM-2026-002');

INSERT INTO chain_of_custody (
    evidence_id, action, from_holder, to_holder, handled_by_staff_id, action_at, location, notes
) VALUES
    (1, 'Collected', 'Dr. A. Wijesinghe', 'Toxicology lab', 3, '2026-05-18 10:00:00', 'Clinical examination room', 'Sealed and labelled.'),
    (1, 'Stored', 'Toxicology lab', 'Lab fridge A2', 3, '2026-05-18 10:15:00', 'Forensic laboratory', 'Seal intact.'),
    (2, 'Collected', 'Dr. A. Wijesinghe', 'Toxicology lab', 3, '2026-05-18 10:05:00', 'Clinical examination room', 'Sealed and labelled.'),
    (3, 'Collected', 'Dr. M. Fernando', 'Histology repository', 3, '2026-05-14 12:20:00', 'Autopsy room', 'Stored pending histology processing.');

INSERT INTO lab_tests (
    test_code, evidence_id, case_id, test_type, requested_at,
    requested_by_staff_id, result, status, report_ref
) VALUES
    ('LAB-2026-001', 1, 2, 'Blood toxicology', '2026-05-18 10:20:00', 1, NULL, 'In Progress', NULL),
    ('LAB-2026-002', 2, 2, 'Urine toxicology', '2026-05-18 10:20:00', 1, NULL, 'Requested', NULL),
    ('LAB-2026-003', 3, 4, 'Histology', '2026-05-14 12:45:00', 2, NULL, 'In Progress', NULL);

INSERT INTO court_reports (
    id, report_no, case_id, report_type, requested_by, requested_at,
    due_date, submission_date, status, prepared_by_staff_id, summary, digital_signature
) VALUES
    (1, 'MLR-2026-001', 1, 'MLR', 'Peradeniya Police', '2026-05-16', '2026-05-25', NULL, 'Drafting', 1, 'Medico-legal report for domestic abuse examination.', 'Dr. A. Wijesinghe / pending final signature'),
    (2, 'MLR-2026-002', 2, 'MLR', 'Kandy Police', '2026-05-18', '2026-05-28', NULL, 'Requested', 1, 'Await toxicology before final opinion.', NULL),
    (3, 'COD-2026-001', 3, 'COD', 'Inquirer into sudden death', '2026-05-11', '2026-05-24', NULL, 'Drafting', 2, 'Cause of death form draft.', 'Dr. M. Fernando / pending final signature'),
    (4, 'PMR-2026-002', 4, 'PMR', 'Kandy Magistrate Court', '2026-05-14', '2026-05-30', NULL, 'Requested', 2, 'PMR pending histology correlation.', NULL);

INSERT INTO notifications (title, message, case_id, report_id, due_date) VALUES
    ('Pending MLR', 'MLEF-2026-002 police copy and MLR are still pending.', 2, 2, '2026-05-28'),
    ('Pending COD', 'COD form for PM-2026-001 requires final issue.', 3, 3, '2026-05-24'),
    ('Court date', 'PM-2026-002 has a court date and histology is still pending.', 4, 4, '2026-05-30');

INSERT INTO audit_logs (actor_user_id, action, entity, entity_id, details) VALUES
    (1, 'seed', 'database', NULL, 'Initial sample forensic medicine department data loaded.');
