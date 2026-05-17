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
