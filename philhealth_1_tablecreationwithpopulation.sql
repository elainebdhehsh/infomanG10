CREATE DATABASE philhealth_1;
USE philhealth_1;


CREATE TABLE MEMBER_TYPES(
member_type CHAR(10) UNIQUE NOT NULL,
description CHAR(50) UNIQUE NOT NULL,
contribution_type CHAR(9) NOT NULL
);

CREATE TABLE MEMBERS(
pin CHAR(12) UNIQUE NOT NULL,
member_name VARCHAR(40) NOT NULL,
date_of_birth DATE NOT NULL,
place_of_birth VARCHAR(70) NOT NULL,
sex CHAR(1) NOT NULL,
civil_status VARCHAR(20) NOT NULL,
citizenship VARCHAR(20) NOT NULL,
philsys_id CHAR(20) UNIQUE,
permanent_address VARCHAR(70) NOT NULL,
mailing_address VARCHAR(70), -- guys i will let you handle the permanent address -> mailing address on frontend
mobile_number CHAR(11) NOT NULL, 
home_phone_number VARCHAR(30), 
business_line VARCHAR(50), 
email_address VARCHAR(50) NOT NULL, 
profession VARCHAR(30),
monthly_income INT,
ssrv_id CHAR(15),
acr_id CHAR(15),
pwd CHAR(20), 
fk_member_type CHAR(10) NOT NULL, 


PRIMARY KEY(pin),

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

CREATE TABLE DEPENDENTS(
dependents_id int AUTO_INCREMENT,
dependents_full_name VARCHAR(40) NOT NULL,
relationship VARCHAR(15) NOT NULL,
dependents_date_of_birth DATE NOT NULL,
dependents_citizenship VARCHAR(15) NOT NULL,
dependent_has_disability TINYINT NOT NULL DEFAULT 0,
fk_pin CHAR(12) NOT NULL,

PRIMARY KEY (dependents_id),

CONSTRAINT fk_pin 
FOREIGN KEY (fk_pin) 
REFERENCES MEMBERS(pin)
ON DELETE RESTRICT
ON UPDATE CASCADE
);

-- Populate --

INSERT INTO MEMBER_TYPES VALUES
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
("PWD", "pwd", "indirect");

INSERT INTO MEMBERS VALUES
('010000000001', 'Juan dela Cruz', '1985-03-12', 'Manila', 'M', 'Married', 'FILIPINO',
 'PSN-0001-0000-0001', '123 Rizal St., Sampaloc, Manila', '123 Rizal St., Sampaloc, Manila',
 '09171234501', '028001001', NULL, 'juan.delacruz@email.com', 'Engineer', 45000,
 NULL, NULL, NULL, 'EMP_PRIV'),
('010000000002', 'Maria Santos', '1990-07-25', 'Quezon City', 'F', 'Single', 'FILIPINO',
 'PSN-0001-0000-0002', '456 Mabini Ave., Diliman, Quezon City', NULL,
 '09281234502', NULL, NULL, 'maria.santos@email.com', 'Teacher', 32000,
 NULL, NULL, NULL, 'EMP_GOV'),
('010000000003', 'Roberto Reyes', '1978-11-05', 'Cebu City', 'M', 'Married', 'FILIPINO',
 'PSN-0001-0000-0003', '789 Osmeña Blvd., Cebu City', '789 Osmeña Blvd., Cebu City',
 '09391234503', '032001003', '032001103', 'roberto.reyes@email.com', 'Doctor', 120000,
 NULL, NULL, NULL, 'PROF_PRAC'),
('010000000004', 'Ana Villanueva', '2000-01-18', 'Davao City', 'F', 'Single', 'FILIPINO',
 NULL, '321 Quirino St., Davao City', NULL,
 '09171234504', NULL, NULL, 'ana.villanueva@email.com', NULL, 18000,
 NULL, NULL, NULL, 'SE_INDIV'),
('010000000005', 'Carlos Mendoza', '1965-09-30', 'Iloilo City', 'M', 'Widow/er', 'FILIPINO',
 'PSN-0001-0000-0005', '654 General Luna St., Iloilo City', '654 General Luna St., Iloilo City',
 '09561234505', '033001005', NULL, 'carlos.mendoza@email.com', NULL, NULL,
 NULL, NULL, NULL, 'SENIOR'),
('010000000006', 'Linda Pascual', '1988-04-14', 'Makati City', 'F', 'Legally Separated', 'DUAL CITIZENSHIP',
 'PSN-0001-0000-0006', '987 Ayala Ave., Makati City', '987 Ayala Ave., Makati City',
 '09881234506', '028001006', '028001106', 'linda.pascual@email.com', 'Accountant', 85000,
 NULL, 'ACR-2024-0006', NULL, 'DUAL_CTZ'),
('010000000007', 'James Thornton', '1975-06-22', 'London, United Kingdom', 'M', 'Married', 'FOREIGN NATIONAL',
 NULL, '111 BGC, Taguig City', '111 BGC, Taguig City',
 '09171234507', '028001007', '028001107', 'james.thornton@email.com', 'Consultant', 200000,
 NULL, 'ACR-2024-0007', NULL, 'FOR_NAT');
 
INSERT INTO DEPENDENTS (dependents_full_name, relationship, dependents_date_of_birth, dependents_citizenship, dependent_has_disability, fk_pin) VALUES
-- Juan dela Cruz (010000000001) - 3 dependents
('Maria dela Cruz','Spouse', '1987-06-15', 'FILIPINO', 0, '010000000001'),
('Miguel dela Cruz','Child', '2010-02-20', 'FILIPINO', 0, '010000000001'),
('Sofia dela Cruz', 'Child', '2013-09-04', 'FILIPINO', 1, '010000000001'),
-- Maria Santos (010000000002) - 2 dependents
('Rosa Santos', 'Parent', '1965-03-11', 'FILIPINO', 0, '010000000002'),
('Pedro Santos', 'Sibling', '1995-08-30', 'FILIPINO', 1, '010000000002'),
-- Roberto Reyes (010000000003) - 2 dependents
('Elena Reyes', 'Spouse', '1980-12-01', 'FILIPINO', 0, '010000000003'),
('Lucas Reyes', 'Child', '2008-05-17', 'FILIPINO', 0, '010000000003'),
-- Ana Villanueva (010000000004) - 1 dependent
('Gloria Villanueva', 'Parent', '1975-07-23', 'FILIPINO', 0, '010000000004'),
-- Carlos Mendoza (010000000005) - 2 dependents
('Isabella Mendoza', 'Child', '1998-04-09', 'FILIPINO', 0, '010000000005'),
('Marco Mendoza', 'Child', '2001-11-25', 'FILIPINO', 0, '010000000005'),
-- James Thornton (010000000007) - 2 dependents
('Claire Thornton', 'Spouse', '1978-03-19', 'FOREIGN',  0, '010000000007'),
('Ethan Thornton', 'Child', '2005-10-08', 'FOREIGN',  0, '010000000007');

-- something i tried --
/*
SELECT * FROM MEMBERS as M;
SELECT * FROM MEMBER_TYPES;

SELECT M.member_name, MT.member_type, MT.description 
FROM MEMBERS as M
LEFT JOIN MEMBER_TYPES as MT
ON  M.fk_member_type = MT.member_type;

SELECT COUNT(*)
FROM MEMBERS
WHERE citizenship LIKE "FILIPINO";

SELECT sex, ROUND(AVG(monthly_income), 2) AS "average monthly income"
FROM MEMBERS
GROUP BY sex
HAVING ROUND(AVG(monthly_income), 2) > 20000;

SELECT M.member_name, MT.member_type, MT.contribution_type, D.dependents_full_name, D.relationship
FROM MEMBERS as M
LEFT JOIN MEMBER_TYPES as MT
ON M.fk_member_type = MT.member_type
LEFT JOIN DEPENDENTS as D
ON M.pin = D.fk_pin;
*/
