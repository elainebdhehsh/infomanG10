
CREATE DATABASE IF NOT EXISTS philhealth_db;
USE philhealth_db;

-- ========================================================
-- 1. REFERENCE TABLE (MEMBER TYPES)
-- ========================================================
CREATE TABLE IF NOT EXISTS MEMBER_TYPES (
    member_type CHAR(10) UNIQUE NOT NULL,
    description CHAR(50) UNIQUE NOT NULL,
    contribution_type CHAR(9) NOT NULL,
    PRIMARY KEY (member_type)
);

-- Default data population
INSERT INTO MEMBER_TYPES (member_type, description, contribution_type) VALUES
("EMP_PRIV", "employed_private", "direct"),
("EMP_GOV", "employed_government", "direct"),
("PROF_PRAC", "professional_practitioner", "direct"),
("SE_INDIV", "self_earning_individual", "direct"),
("SE_SOLE", "self_earning_sole_proprietor", "direct"),
("SE_GROUP", "self_earning_group_enrollement_scheme", "direct"),
("KASAM", "kasambahay", "direct"),
("FAM_DRV", "family_driver", "direct"),
("MIG_LAND", "migrant_worker_land_based", "direct"),
("MIG_SEA", "migrant_worker_sea_based", "direct"),
("LIFETIME", "lifetime_member", "direct"),
("DUAL_CTZ", "filipinos_with_dual_citizenship_living_abroad", "direct"),
("FOR_NAT", "foreign_national", "direct"),
("LISTA", "listahanan", "indirect"),
("MCCT_4PS", "4Ps_MCCT", "indirect"),
("SENIOR", "senior_citizen", "indirect"),
("PAMANA", "pamana", "indirect"),
("KIA_KIPO", "kia_kipo", "indirect"),
("BANGSA", "bangsamoro_normalization", "indirect"),
("LGU_SPON", "lgu_sponsored", "indirect"),
("NGA_SPON", "nga_sponsored", "indirect"),
("PRIV_SPON", "private_sponsored", "indirect"),
("PWD", "pwd", "indirect")
ON DUPLICATE KEY UPDATE 
description=VALUES(description), 
contribution_type=VALUES(contribution_type);

-- ========================================================
-- 2. MEMBERS TABLE
-- ========================================================
CREATE TABLE IF NOT EXISTS members (
    pin CHAR(12) NOT NULL,
    member_name VARCHAR(40) NOT NULL,
    date_of_birth DATE NOT NULL,
    place_of_birth VARCHAR(70) NOT NULL,
    sex CHAR(1) NOT NULL,
    civil_status VARCHAR(20) NOT NULL,
    citizenship VARCHAR(20) NOT NULL,
    philsys_id CHAR(20) UNIQUE,
    permanent_address VARCHAR(70) NOT NULL,
    mailing_address VARCHAR(70),
    mobile_number CHAR(11) NOT NULL,
    home_phone_number VARCHAR(30),
    business_line VARCHAR(50),
    email_address VARCHAR(50) NOT NULL,
    profession VARCHAR(30),
    monthly_income INT,
    srrv_id CHAR(15),
    acr_id CHAR(15),
    pwd_id CHAR(20),
    mother_fullname VARCHAR(40) NOT NULL,      -- Required constraint dictionary item
    spouse_fullname VARCHAR(40),
    fk_member_type CHAR(10) NOT NULL,          -- Reverted to CHAR(10) to match MEMBER_TYPES

    PRIMARY KEY(pin),

    -- Robust Validation Constraints from philhealth_1
    CONSTRAINT chk_sex CHECK (sex IN ('M', 'F')),
    CONSTRAINT chk_civil_status CHECK (civil_status IN ('Single', 'Married', 'Widow/er', 'Annulled', 'Legally Separated')),
    CONSTRAINT chk_citizenship CHECK (citizenship IN ('FILIPINO', 'FOREIGN NATIONAL', 'DUAL CITIZENSHIP')),
    CONSTRAINT chk_mobile_number CHECK (mobile_number LIKE '09%'),
    CONSTRAINT chk_email_address CHECK (email_address LIKE '%@%.%'),
    CONSTRAINT chk_monthly_income CHECK (monthly_income > 0),

    CONSTRAINT fk_member_type
	FOREIGN KEY (fk_member_type) 
	REFERENCES MEMBER_TYPES(member_type)
	ON DELETE RESTRICT
	ON UPDATE CASCADE
);

-- Address Sync Trigger (Keeps full address up to VARCHAR(70))
DELIMITER //
CREATE TRIGGER before_members_insert
BEFORE INSERT ON members
FOR EACH ROW
BEGIN
    IF NEW.mailing_address IS NULL OR NEW.mailing_address = '' THEN
        SET NEW.mailing_address = NEW.permanent_address;
    END IF;
END;
//
CREATE TRIGGER before_members_update
BEFORE UPDATE ON members
FOR EACH ROW
BEGIN
    IF NEW.mailing_address IS NULL OR NEW.mailing_address = '' THEN
        SET NEW.mailing_address = NEW.permanent_address;
    END IF;
END;
//
DELIMITER ;

-- ========================================================
-- 3. DEPENDENTS TABLE (Allows multiple rows per member pin)
-- ========================================================
CREATE TABLE IF NOT EXISTS dependents (
    dependents_id INT AUTO_INCREMENT,
    dependents_full_name VARCHAR(40) NOT NULL,
    relationship VARCHAR(15) NOT NULL,
    dependents_date_of_birth DATE NOT NULL,
    dependents_citizenship VARCHAR(15) NOT NULL,
    dependent_has_disability BOOLEAN NOT NULL DEFAULT FALSE,
    fk_pin CHAR(12) NOT NULL,                  

    PRIMARY KEY (dependents_id),
    CONSTRAINT fk_pin 
	FOREIGN KEY (fk_pin) 
	REFERENCES members(pin)
	ON DELETE RESTRICT
	ON UPDATE CASCADE
);


INSERT INTO members VALUES
-- 1. Employed Private | Filipino | Male | Married | Engineer
('010000000001', 'Juan dela Cruz',    '1985-03-12', 'Manila',                'M', 'Married',           'FILIPINO',
 'PSN-0001-0000-0001', '123 Rizal St., Sampaloc, Manila',       NULL,
 '09171234501', '028001001', NULL,        'juan.delacruz@email.com',   'Engineer',        45000,
 NULL, NULL, NULL, 'Teresa dela Cruz',   'Maria dela Cruz',   'EMP_PRIV'),

-- 2. Employed Government | Filipino | Female | Single | Teacher
('010000000002', 'Maria Santos',      '1990-07-25', 'Quezon City',           'F', 'Single',            'FILIPINO',
 'PSN-0001-0000-0002', '456 Mabini Ave., Diliman, Quezon City', NULL,
 '09281234502', NULL,        NULL,        'maria.santos@email.com',    'Teacher',         32000,
 NULL, NULL, NULL, 'Corazon Santos',     NULL,                'EMP_GOV'),

-- 3. Professional Practitioner | Filipino | Male | Married | Doctor
('010000000003', 'Roberto Reyes',     '1978-11-05', 'Cebu City',             'M', 'Married',           'FILIPINO',
 'PSN-0001-0000-0003', '789 Osmeña Blvd., Cebu City',          NULL,
 '09391234503', '032001003', '032001103', 'roberto.reyes@email.com',   'Doctor',         120000,
 NULL, NULL, NULL, 'Remedios Reyes',     'Elena Reyes',       'PROF_PRAC'),

-- 4. Self-Earning Individual | Filipino | Female | Single | Freelancer
('010000000004', 'Ana Villanueva',    '2000-01-18', 'Davao City',            'F', 'Single',            'FILIPINO',
 NULL,                 '321 Quirino St., Davao City',           NULL,
 '09171234504', NULL,        NULL,        'ana.villanueva@email.com',  'Freelancer',      18000,
 NULL, NULL, NULL, 'Gloria Villanueva',  NULL,                'SE_INDIV'),

-- 5. Senior Citizen | Filipino | Male | Widow/er | Retired
--    NOTE: Children are adults (born ~1985–1990), no qualified dependents
('010000000005', 'Carlos Mendoza',    '1955-09-30', 'Iloilo City',           'M', 'Widow/er',          'FILIPINO',
 'PSN-0001-0000-0005', '654 General Luna St., Iloilo City',    NULL,
 '09561234505', '033001005', NULL,        'carlos.mendoza@email.com',  NULL,               NULL,
 NULL, NULL, NULL, 'Felicidad Mendoza',  NULL,                'SENIOR'),

-- 6. Dual Citizenship | Female | Legally Separated | Accountant
--    NOTE: Legally Separated — spouse NOT a qualified dependent
('010000000006', 'Linda Pascual',     '1988-04-14', 'Makati City',           'F', 'Legally Separated', 'DUAL CITIZENSHIP',
 'PSN-0001-0000-0006', '987 Ayala Ave., Makati City',          NULL,
 '09881234506', '028001006', '028001106', 'linda.pascual@email.com',   'Accountant',      85000,
 NULL, 'ACR-2024-0006', NULL, 'Rosario Pascual', NULL,         'DUAL_CTZ'),

-- 7. Foreign National | Male | Married | Consultant
--    RULE: FOR_NAT must have acr_id
('010000000007', 'James Thornton',    '1975-06-22', 'London, United Kingdom','M', 'Married',           'FOREIGN NATIONAL',
 NULL,                 '111 BGC Ave., Taguig City',             NULL,
 '09171234507', '028001007', '028001107', 'james.thornton@email.com',  'Consultant',     200000,
 NULL, 'ACR-2024-0007', NULL, 'Margaret Thornton',  'Claire Thornton',   'FOR_NAT'),

-- 8. Kasambahay | Filipino | Female | Single | Household Worker
--    NOTE: Reflects NCR kasambahay minimum wage (~₱6,000)
('010000000008', 'Rosario Bautista',  '1998-05-10', 'Batangas City',         'F', 'Single',            'FILIPINO',
 NULL,                 'B12 L5 Sunset Homes, Las Pinas City',  NULL,
 '09451234508', NULL,        NULL,        'rosario.bautista@email.com','Household Worker',  6000,
 NULL, NULL, NULL, 'Natividad Bautista', NULL,                'KASAM'),

-- 9. Migrant Worker Sea-Based | Filipino | Male | Married | Seafarer
('010000000009', 'Eduardo Navarro',   '1982-08-19', 'Batangas City',         'M', 'Married',           'FILIPINO',
 'PSN-0001-0000-0009', '22 Dalisay St., Batangas City',        NULL,
 '09321234509', '043001009', NULL,        'eduardo.navarro@email.com', 'Seafarer',        95000,
 NULL, NULL, NULL, 'Caridad Navarro',    'Liza Navarro',      'MIG_SEA'),

-- 10. PWD | Filipino | Male | Single
--     RULE: PWD member type must have pwd_id
('010000000010', 'Fernando Garcia',   '1993-12-03', 'Pasig City',            'M', 'Single',            'FILIPINO',
 'PSN-0001-0000-0010', '45 Ortigas Ave., Pasig City',          NULL,
 '09201234510', NULL,        NULL,        'fernando.garcia@email.com', NULL,               8000,
 NULL, NULL, 'PWD-2020-001234', 'Ligaya Garcia', NULL,         'PWD');



INSERT INTO dependents (dependents_full_name, relationship, dependents_date_of_birth, dependents_citizenship, dependent_has_disability, fk_pin) VALUES

-- Juan dela Cruz (010000000001) — 3 dependents
-- spouse_fullname in MEMBERS matches this Spouse entry
('Maria dela Cruz',    'Spouse', '1987-06-15', 'FILIPINO', 0, '010000000001'),
('Miguel dela Cruz',   'Child',  '2012-02-20', 'FILIPINO', 0, '010000000001'),
('Sofia dela Cruz',    'Child',  '2016-09-04', 'FILIPINO', 1, '010000000001'), 

-- Maria Santos (010000000002) — 1 dependent
('Rosa Santos',        'Parent', '1965-03-11', 'FILIPINO', 0, '010000000002'),

-- Roberto Reyes (010000000003) — 3 dependents
('Elena Reyes',        'Spouse', '1980-12-01', 'FILIPINO', 0, '010000000003'),
('Lucas Reyes',        'Child',  '2010-05-17', 'FILIPINO', 0, '010000000003'),
('Clara Reyes',        'Child',  '2014-08-22', 'FILIPINO', 0, '010000000003'),

-- Linda Pascual (010000000006) — 2 dependents
-- Legally Separated — spouse is NOT a dependent, children only
('Gabrielle Pascual',  'Child',  '2013-07-09', 'FILIPINO', 0, '010000000006'),
('Noah Pascual',       'Child',  '2016-11-15', 'FILIPINO', 0, '010000000006'),

-- James Thornton (010000000007) — 2 dependents
-- Foreign family, citizenship tagged as 'FOREIGN'
('Claire Thornton',    'Spouse', '1978-03-19', 'FOREIGN',  0, '010000000007'),
('Ethan Thornton',     'Child',  '2008-10-08', 'FOREIGN',  0, '010000000007'), 

-- Eduardo Navarro (010000000009) — 3 dependents
('Liza Navarro',       'Spouse', '1985-04-12', 'FILIPINO', 0, '010000000009'),
('Diego Navarro',      'Child',  '2011-01-30', 'FILIPINO', 0, '010000000009'),
('Isabella Navarro',   'Child',  '2015-06-18', 'FILIPINO', 0, '010000000009'),

-- Fernando Garcia (010000000010) — 1 dependent
-- Single, no children → Parent registration is valid
-- mother_fullname in MEMBERS intentionally matches this entry
('Ligaya Garcia',      'Parent', '1968-09-22', 'FILIPINO', 0, '010000000010');