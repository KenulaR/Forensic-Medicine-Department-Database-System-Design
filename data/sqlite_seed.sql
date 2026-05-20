PRAGMA foreign_keys = ON;

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
    (1, 'MLEF-2026-001', '2026-05-16 14:30', 'Patient alleges assault by spouse.', 'Patient conscious, oriented, anxious.', 'Bruising over left forearm and right shoulder.', 'X-ray requested. No fracture reported.', 'Psychiatry referral requested.', 'Outpatient review in 7 days.', 'storage/clinical/CL-2026-001/photos', 1, 'Drafted', '2026-06-05'),
    (2, 'MLEF-2026-002', '2026-05-18 09:15', 'Detainee brought by police for examination.', 'No acute distress. Old scar noted.', 'No fresh external injuries.', 'Blood and urine toxicology sent.', NULL, 'Awaiting toxicology.', 'storage/clinical/CL-2026-002/photos', 0, 'Pending', '2026-05-28');

INSERT INTO postmortems (
    case_id, pmr_no, death_type, inquest_order_no, autopsy_date,
    pre_autopsy_info, external_findings, internal_findings, cause_of_death,
    cod_status, histology_status, photos_path, audio_transcript_ref, next_court_date
) VALUES
    (3, 'PMR-2026-001', 'Natural', 'INQ/KDY/2026/088', '2026-05-11 10:00', 'BHT reviewed. Family statement recorded.', 'No external injuries of medico-legal significance.', 'Severe coronary artery atherosclerosis.', 'Ischaemic heart disease', 'Drafted', 'Not Required', 'storage/autopsy/PM-2026-001/photos', 'storage/autopsy/PM-2026-001/audio-transcript.txt', '2026-06-12'),
    (4, 'PMR-2026-002', 'Undetermined', 'CRT/KDY/2026/044', '2026-05-14 11:30', 'Crime scene photographs and police statements received.', 'Multiple abrasions noted.', 'Internal examination pending histology correlation.', NULL, 'Pending', 'Pending', 'storage/autopsy/PM-2026-002/photos', NULL, '2026-05-30');

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
    (1, 'EVD-2026-001', 2, 'Blood sample', 'Blood sample for toxicology.', '2026-05-18 10:00', 3, 'Lab fridge A2', 'Pending', 'EVD-2026-001|CL-2026-002'),
    (2, 'EVD-2026-002', 2, 'Urine sample', 'Urine sample for toxicology.', '2026-05-18 10:05', 3, 'Lab fridge A2', 'Pending', 'EVD-2026-002|CL-2026-002'),
    (3, 'EVD-2026-003', 4, 'Histology tissue block', 'Tissue sample retained for histology.', '2026-05-14 12:20', 3, 'Histology shelf H1', 'Pending', 'EVD-2026-003|PM-2026-002');

INSERT INTO chain_of_custody (
    evidence_id, action, from_holder, to_holder, handled_by_staff_id, action_at, location, notes
) VALUES
    (1, 'Collected', 'Dr. A. Wijesinghe', 'Toxicology lab', 3, '2026-05-18 10:00', 'Clinical examination room', 'Sealed and labelled.'),
    (1, 'Stored', 'Toxicology lab', 'Lab fridge A2', 3, '2026-05-18 10:15', 'Forensic laboratory', 'Seal intact.'),
    (2, 'Collected', 'Dr. A. Wijesinghe', 'Toxicology lab', 3, '2026-05-18 10:05', 'Clinical examination room', 'Sealed and labelled.'),
    (3, 'Collected', 'Dr. M. Fernando', 'Histology repository', 3, '2026-05-14 12:20', 'Autopsy room', 'Stored pending histology processing.');

INSERT INTO lab_tests (
    test_code, evidence_id, case_id, test_type, requested_at,
    requested_by_staff_id, result, status, report_ref
) VALUES
    ('LAB-2026-001', 1, 2, 'Blood toxicology', '2026-05-18 10:20', 1, NULL, 'In Progress', NULL),
    ('LAB-2026-002', 2, 2, 'Urine toxicology', '2026-05-18 10:20', 1, NULL, 'Requested', NULL),
    ('LAB-2026-003', 3, 4, 'Histology', '2026-05-14 12:45', 2, NULL, 'In Progress', NULL);

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
