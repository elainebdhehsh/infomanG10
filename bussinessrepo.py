from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Database connection settings
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "NewPass",        # replace with your actual password
    "database": "philhealth_db"
}

# Reports dictionary
reports = {
    "Q1": {
        "title": "Member Contact Directory",
        "description": "Personnel reference for reaching out to members",
        "sql": """SELECT pin, member_name, mobile_number, email_address, permanent_address
                  FROM members ORDER BY member_name;"""
    },
    "Q2": {
        "title": "Members with Missing PhilSys ID",
        "description": "Tracks members not yet linked to the national ID system",
        "sql": """SELECT pin, member_name, email_address, mobile_number, fk_member_type
                  FROM members WHERE philsys_id IS NULL ORDER BY member_name;"""
    },
    "Q3": {
        "title": "Members in High Income Bracket",
        "description": "Flags members earning above ₱50,000 for contribution bracket verification",
        "sql": """SELECT member_name, profession, monthly_income, fk_member_type
                  FROM members WHERE monthly_income > 50000 ORDER BY monthly_income DESC;"""
    },
    "Q4": {
        "title": "Member Count by Civil Status",
        "description": "Demographic overview",
        "sql": """SELECT civil_status, COUNT(*) AS total_members
                  FROM members GROUP BY civil_status ORDER BY total_members DESC;"""
    },
    "Q5": {
        "title": "Member Types with Average Monthly Income Above ₱30,000",
        "description": "Contribution analysis per membership category",
        "sql": """SELECT fk_member_type, ROUND(AVG(monthly_income), 2) AS avg_monthly_income, COUNT(*) AS member_count
                  FROM members
                  WHERE monthly_income IS NOT NULL
                  GROUP BY fk_member_type
                  HAVING avg_monthly_income > 30000
                  ORDER BY avg_monthly_income DESC;"""
    },
    "Q6": {
        "title": "Members with 2 or More Registered Dependents",
        "description": "Coverage load report",
        "sql": """SELECT fk_pin, COUNT(*) AS dependent_count
                  FROM dependents
                  GROUP BY fk_pin
                  HAVING dependent_count >= 2
                  ORDER BY dependent_count DESC;"""
    },
    "Q7": {
        "title": "Full Member Registry with Type Classification",
        "description": "Complete member profile report showing contribution classification and personal info",
        "sql": """SELECT m.pin, m.member_name, m.civil_status, m.monthly_income, mt.description AS member_type, mt.contribution_type
                  FROM members m
                  JOIN member_types mt ON m.fk_member_type = mt.member_type
                  ORDER BY m.member_name;"""
    },
    "Q8": {
        "title": "Dependent Registry per Member",
        "description": "Beneficiary report (member and dependents)",
        "sql": """SELECT m.member_name, m.civil_status, d.dependents_full_name, d.relationship, d.dependents_date_of_birth, d.dependents_citizenship
                  FROM members m
                  JOIN dependents d ON m.pin = d.fk_pin
                  ORDER BY m.member_name, d.relationship;"""
    },
    "Q9": {
        "title": "Members Enrolled Under Government Subsidized Programs",
        "description": "Subsidy tracking report (Indirect Incomes)",
        "sql": """SELECT m.pin, m.member_name, mt.description AS program_name, m.mobile_number, m.email_address
                  FROM members m
                  JOIN member_types mt ON m.fk_member_type = mt.member_type
                  WHERE mt.contribution_type = 'indirect'
                  ORDER BY mt.description, m.member_name;"""
    },
    "Q10": {
        "title": "Enrollment Overview per Member Type",
        "description": "Shows count of members and dependents on each member type",
        "sql": """SELECT mt.description AS member_type, mt.contribution_type, COUNT(DISTINCT m.pin) AS total_members, COUNT(d.dependents_id) AS total_dependents
                  FROM member_types mt
                  JOIN members m ON mt.member_type = m.fk_member_type
                  JOIN dependents d ON m.pin = d.fk_pin
                  GROUP BY mt.description, mt.contribution_type
                  ORDER BY total_members DESC;"""
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
