CREATE DATABASE IF NOT EXISTS philhealth_db;
USE philhealth_db;

CREATE TABLE IF NOT EXISTS contribution_type (
    member_type CHAR(35) PRIMARY KEY UNIQUE NOT NULL,
    contribution_type CHAR(9) NOT NULL
);

INSERT INTO contribution_type (member_type, contribution_type) VALUES
('Employed Private', 'Direct'),
('Employed Government', 'Direct'),
('Professional Practitioner', 'Direct'),
('Self-Earning Individual', 'Direct'),
('Individual', 'Direct'),
('Sole Proprietor', 'Direct'),
('Group Enrollment Scheme', 'Direct'),
('Kasambahay', 'Direct'),
('Migrant Worker', 'Direct'),
('Land-Based', 'Direct'),
('Sea-Based', 'Direct'),
('Family Driver', 'Direct'),
('Lifetime Member', 'Direct'),
('Filipinos with Dual Citizenship', 'Direct'),
('Foreign National', 'Direct'),
('Listahanan', 'Indirect'),
('4Ps/MCCT', 'Indirect'),
('Senior Citizen', 'Indirect'),
('PAMANA', 'Indirect'),
('KIA/KIPO', 'Indirect'),
('Bangsamoro/Normalization', 'Indirect'),
('LGU-sponsored', 'Indirect'),
('NGA-sponsored', 'Indirect'),
('Private-sponsored', 'Indirect'),
('Person with Disability', 'Indirect')
ON DUPLICATE KEY UPDATE contribution_type=VALUES(contribution_type);

CREATE TABLE IF NOT EXISTS members (
    pin CHAR(12) PRIMARY KEY UNIQUE NOT NULL,
    member_name VARCHAR(40) NOT NULL,
    date_of_birth DATE NOT NULL,
    place_of_birth VARCHAR(50) NOT NULL,
    sex CHAR(1) NOT NULL,
    civil_status VARCHAR(20) NOT NULL,
    citizenship VARCHAR(18) NOT NULL,
    permanent_address VARCHAR(70) NOT NULL,
    mailing_address VARCHAR(20),
    mobile_number CHAR(11) NOT NULL,
    home_phone_number VARCHAR(50),
    bussiness_line VARCHAR(50),
    email_address VARCHAR(20) NOT NULL,
    profession VARCHAR(30),
    monthly_income INT,
    philsys_id CHAR(20) UNIQUE,
    srrv_id CHAR(15),
    acr_id CHAR(15),
    pwd_id CHAR(20),
    mother_fullname VARCHAR(40) NOT NULL,
    spouse_fullname VARCHAR(40),
    member_type CHAR(35) UNIQUE NOT NULL,
    FOREIGN KEY (member_type) REFERENCES contribution_type(member_type)
);

-- Derived column logic (Trigger based since generated columns can't use IFNULL with same input)
DELIMITER //
CREATE TRIGGER before_members_insert
BEFORE INSERT ON members
FOR EACH ROW
BEGIN
    IF NEW.mailing_address IS NULL OR NEW.mailing_address = '' THEN
        SET NEW.mailing_address = SUBSTRING(NEW.permanent_address, 1, 20);
    END IF;
END;
//
CREATE TRIGGER before_members_update
BEFORE UPDATE ON members
FOR EACH ROW
BEGIN
    IF NEW.mailing_address IS NULL OR NEW.mailing_address = '' THEN
        SET NEW.mailing_address = SUBSTRING(NEW.permanent_address, 1, 20);
    END IF;
END;
//
DELIMITER ;

CREATE TABLE IF NOT EXISTS dependents (
    dependents_id INT PRIMARY KEY AUTO_INCREMENT,
    dependents_full_name VARCHAR(40) NOT NULL,
    relationship VARCHAR(15) NOT NULL,
    dependents_date_of_birth DATE NOT NULL,
    dependents_citizenship VARCHAR(15) NOT NULL,
    dependent_has_disability BOOLEAN,
    pin CHAR(12) UNIQUE NOT NULL,
    FOREIGN KEY (pin) REFERENCES members(pin)
);
