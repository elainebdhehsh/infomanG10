from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Database connection settings
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1235",        # replace with your actual password
    "database": "philhealth_db"
}

# Reports dictionary
reports = {
    "Q1": {
        "title": "Member Contact Directory",
        "description": "Personnel reference for reaching out to members",
        "sql": """SELECT pin AS PIN, member_name AS Name, mobile_number AS "Mobile Number", email_address AS Email, permanent_address AS "Permanent Address"
                  FROM members ORDER BY member_name;"""
    },
    "Q2": {
        "title": "Members with Missing PhilSys ID",
        "description": "Tracks members not yet linked to the national ID system",
        "sql": """SELECT pin AS PIN, member_name AS Name, email_address AS Email, mobile_number AS "Mobile Number", fk_member_type AS "Member_Type"
                  FROM members WHERE philsys_id IS NULL ORDER BY member_name;"""
    },
    "Q3": {
        "title": "Members in High Income Bracket",
        "description": "Flags members earning above ₱50,000 for contribution bracket verification",
        "sql": """SELECT member_name AS Name, profession AS Profession, monthly_income AS "Monthly Income", fk_member_type AS "Member Type"
                  FROM members WHERE monthly_income > 50000 ORDER BY monthly_income DESC;"""
    },
    "Q4": {
        "title": "Member Count by Civil Status",
        "description": "Demographic overview",
        "sql": """SELECT civil_status AS "Civil Status", COUNT(*) AS "Total Members"
                  FROM members GROUP BY civil_status ORDER BY "Total Members" DESC;"""
    },
    "Q5": {
        "title": "Member Types with Average Monthly Income Above ₱30,000",
        "description": "Contribution analysis per membership category",
        "sql": """SELECT fk_member_type AS "Member Type", ROUND(AVG(monthly_income), 2) AS "Average Monthly Income", COUNT(*) AS member_count
                  FROM members
                  WHERE monthly_income IS NOT NULL
                  GROUP BY fk_member_type
                  HAVING AVG(monthly_income) > 30000
                  ORDER BY "Average Monthly Income" DESC;"""
    },
    "Q6": {
        "title": "Members with 2 or More Registered Dependents",
        "description": "Coverage load report",
        "sql": """SELECT fk_pin AS PIN, m.member_name AS Name, COUNT(*) AS "Dependent Count"
                  FROM dependents AS d
                  JOIN members AS m
                  ON m.pin = d.fk_pin
                  GROUP BY fk_pin
                  HAVING COUNT(*) >= 2
                  ORDER BY "Dependent Count" DESC;"""
    },
    "Q7": {
        "title": "Full Member Registry with Type Classification",
        "description": "Complete member profile report showing contribution classification and personal info",
        "sql": """SELECT m.pin AS PIN, m.member_name AS Name, m.civil_status AS "Civil Status", m.monthly_income AS "Monthly Income", mt.description AS "Member Type", mt.contribution_type AS "Contribution Type"
                  FROM members m
                  JOIN member_types mt ON m.fk_member_type = mt.member_type
                  ORDER BY Name;"""
    },
    "Q8": {
        "title": "Dependent Registry per Member",
        "description": "Beneficiary report (member and dependents)",
        "sql": """SELECT m.member_name AS Name, 
       m.civil_status AS "Civil Status", 
       d.dependents_full_name AS "Dependents Name", 
       d.relationship AS Relationship, 
       d.dependents_date_of_birth AS Birthdate, 
       d.dependents_citizenship AS Citizenship
        FROM members m
        JOIN dependents d ON m.pin = d.fk_pin
        ORDER BY Name, Relationship;"""
    },
    "Q9": {
        "title": "Members Enrolled Under Government Subsidized Programs",
        "description": "Subsidy tracking report (Indirect Incomes)",
        "sql": """SELECT m.pin AS PIN, m.member_name AS Name, mt.description AS "Program Name", m.mobile_number AS "Mobile Numer", m.email_address AS Email
                  FROM members m
                  JOIN member_types mt ON m.fk_member_type = mt.member_type
                  WHERE mt.contribution_type = 'indirect'
                  ORDER BY "Program Name", Name;"""
    },
    "Q10": {
        "title": "Enrollment Overview per Member Type",
        "description": "Shows count of members and dependents on each member type",
        "sql": """SELECT mt.description AS "Member Type", 
       mt.contribution_type AS "Contribution Type", 
       COUNT(DISTINCT m.pin) AS "Total Members", 
       COUNT(d.dependents_id) AS "Total Dependents"
        FROM member_types mt
        JOIN members m ON mt.member_type = m.fk_member_type
        JOIN dependents d ON m.pin = d.fk_pin
        GROUP BY mt.description, mt.contribution_type
        ORDER BY "Total Members" DESC;"""
    }
}

@app.route("/")
def reports_page():
    selected = request.args.get("report")
    report = None
    rows = []
    headers = []

    if selected and selected in reports:
        report = reports[selected]
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(report["sql"])
        rows = cursor.fetchall()
        headers = [i[0] for i in cursor.description]
        cursor.close()
        conn.close()

    return render_template("report.html", report=report, rows=rows, headers=headers)

if __name__ == "__main__":
    app.run(debug=True)
