-- PostgreSQL Schema for Prescription Data Capture

CREATE TABLE IF NOT EXISTS run_audit (
    run_id UUID PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20),
    emails_processed INT DEFAULT 0,
    records_stored INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS prescriptions (
    id SERIAL PRIMARY KEY,
    prescription_number VARCHAR(50) NOT NULL,
    dispensing_date DATE NOT NULL,
    patient_name VARCHAR(255),
    drug_name VARCHAR(255),
    day_supply INT,
    total_amount DECIMAL(10, 2),
    drug_type VARCHAR(100),
    brand_indicator BOOLEAN,
    daw VARCHAR(50),
    origin VARCHAR(100),
    prescriber_name VARCHAR(255),
    status VARCHAR(50),
    refill_auth VARCHAR(100),
    order_date DATE,
    dob DATE,
    sex CHAR(1),
    lot_number VARCHAR(100),
    patient_type VARCHAR(100),
    drug_class VARCHAR(100),
    npi VARCHAR(20),
    license VARCHAR(50),
    indicator_340b BOOLEAN,
    quantity DECIMAL(10, 2),
    original_email_path VARCHAR(255),
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(prescription_number, dispensing_date)
);

CREATE INDEX IF NOT EXISTS idx_prescriptions_rx_date ON prescriptions(prescription_number, dispensing_date);
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_name);

CREATE TABLE IF NOT EXISTS email_audit (
    email_id VARCHAR(100) PRIMARY KEY,
    subject VARCHAR(255),
    received_date TIMESTAMP,
    status VARCHAR(50),
    error_message TEXT,
    run_id UUID REFERENCES run_audit(run_id),
    original_email_path VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_email_audit_run ON email_audit(run_id);
CREATE INDEX IF NOT EXISTS idx_email_audit_status ON email_audit(status);
);
