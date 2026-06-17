import re
import random
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'philhealth_multistep_secure_token_v6'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="NewPass",
        database="philhealth_db"
    )

def sanitize_field(val, is_numeric=False, max_len=None):
    if val is None or str(val).strip() == '':
        return None
    if is_numeric:
        cleaned = re.sub(r'[^\d.]', '', str(val))
        if not cleaned:
            return None
        try:
            num = int(float(cleaned))
            return num if num > 0 else None
        except ValueError:
            return None
    val = str(val).strip()
    if max_len:
        val = val[:max_len]
    return val

def construct_address_string(data_dict, prefix):
    parts = [
        data_dict.get(f'{prefix}_unit', ''),
        data_dict.get(f'{prefix}_lot', ''),
        data_dict.get(f'{prefix}_street', ''),
        data_dict.get(f'{prefix}_subdivision', ''),
        data_dict.get(f'{prefix}_barangay', ''),
        data_dict.get(f'{prefix}_city', ''),
        data_dict.get(f'{prefix}_province', ''),
        data_dict.get(f'{prefix}_zip', '')
    ]
    full_address = ", ".join([p.strip() for p in parts if p and str(p).strip()])
    return full_address[:70]

def build_full_name(p2):
    last = (p2.get('last_name') or '').strip()
    first = (p2.get('first_name') or '').strip()
    middle = '' if p2.get('no_middle_name') else (p2.get('middle_name') or '').strip()
    suffix = '' if p2.get('no_extension') else (p2.get('suffix') or '').strip()
    if p2.get('mononym'):
        full = last or first
    else:
        full = " ".join(p for p in [first, middle, last, suffix] if p)
    full = re.sub(r'\s+', ' ', full).strip()
    return full[:40] if full else None

def build_mother_fullname(p2):
    last = (p2.get('mother_last_name') or '').strip()
    first = (p2.get('mother_first_name') or '').strip()
    if not last and not first:
        return 'N/A'
    name = ", ".join(p for p in [last, first] if p)
    return name[:40]

def build_spouse_fullname(p2):
    last = (p2.get('spouse_last_name') or '').strip()
    first = (p2.get('spouse_first_name') or '').strip()
    if not last and not first:
        return None
    name = ", ".join(p for p in [last, first] if p)
    return name[:40]

SEX_MAP = {'Male': 'M', 'Female': 'F'}

CITIZENSHIP_MAP = {
    'Filipino': 'FILIPINO',
    'Dual Citizen': 'DUAL CITIZENSHIP',
    'Foreign National': 'FOREIGN NATIONAL'
}

def normalize_mobile(raw):
    if not raw:
        return None
    digits = re.sub(r'[^0-9+]', '', raw)
    if digits.startswith('+63'):
        digits = '0' + digits[3:]
    elif digits.startswith('63') and len(digits) == 12:
        digits = '0' + digits[2:]
    return digits[:11] if digits else None

MEMBER_TYPE_MAP = {
    'Employed Private': 'EMP_PRIV',
    'Employed Government': 'EMP_GOV',
    'Professional Practitioner': 'PROF_PRAC',
    'Self-Earning Individual': 'SE_INDIV',
    'Individual': 'SE_INDIV',
    'Sole Proprietor': 'SE_SOLE',
    'Group Enrollment Scheme': 'SE_GROUP',
    'Kasambahay': 'KASAM',
    'Family Driver': 'FAM_DRV',
    'Lifetime Member': 'LIFETIME',
    'Dual Citizenship / Living Abroad': 'DUAL_CTZ',
    'Foreign National': 'FOR_NAT',
    'Listahanan': 'LISTA',
    '4Ps / MCCT': 'MCCT_4PS',
    'Senior Citizen': 'SENIOR',
    'PAMANA': 'PAMANA',
    'KIA / KIPO': 'KIA_KIPO',
    'Bangsamoro': 'BANGSA',
    'LGU-sponsored': 'LGU_SPON',
    'NGA-sponsored': 'NGA_SPON',
    'Private-sponsored': 'PRIV_SPON',
    'Person with Disability': 'PWD',
}

def resolve_member_type(p5):
    status = (p5.get('member_type_status') or '').strip()
    if status == 'Migrant Worker':
        sub_types = p5.get('migrant_type_list') or []
        if 'Sea-Based' in sub_types:
            return 'MIG_SEA'
        if 'Land-Based' in sub_types:
            return 'MIG_LAND'
        return None
    return MEMBER_TYPE_MAP.get(status)

def generate_unique_pin(cursor):
    for _ in range(25):
        candidate = ''.join(str(random.randint(0, 9)) for _ in range(12))
        cursor.execute("SELECT 1 FROM members WHERE pin = %s", (candidate,))
        if cursor.fetchone() is None:
            return candidate
    raise Error("Could not generate a unique PIN. Please try submitting again.")

@app.route("/records")
def records():
    conn = None
    members = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT pin, member_name, permanent_address,
                   date_of_birth, sex, civil_status, citizenship
            FROM members
            ORDER BY member_name ASC
        """)
        members = cursor.fetchall()
        cursor.close()
    except Error as e:
        flash(f"Database error: {str(e)}", "error")
    finally:
        if conn and conn.is_connected():
            conn.close()
    return render_template("records.html", members=members)

@app.route("/view/<pin>")
def view_record(pin):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM members WHERE pin = %s", (pin,))
        member = cursor.fetchone()
        if not member:
            flash(f"No record found for PIN {pin}.", "error")
            return redirect(url_for("records"))
        cursor.execute("SELECT * FROM dependents WHERE fk_pin = %s", (pin,))
        dependents = cursor.fetchall()
        cursor.close()
        members = [member]
        return render_template("records.html", members=members, view_mode=True, dependents=dependents)
    except Error as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect(url_for("records"))
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route("/delete/<pin>", methods=["POST"])
def delete_record(pin):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dependents WHERE fk_pin = %s", (pin,))
        cursor.execute("DELETE FROM members WHERE pin = %s", (pin,))
        conn.commit()
        cursor.close()
        flash(f"Member with PIN {pin} has been successfully deleted.", "success")
    except Error as e:
        if conn:
            conn.rollback()
        flash(f"Database error while deleting: {str(e)}", "error")
    finally:
        if conn and conn.is_connected():
            conn.close()
    return redirect(url_for("records"))

@app.route("/edit/<pin>")
def edit_record(pin):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM members WHERE pin = %s", (pin,))
        member = cursor.fetchone()
        if not member:
            flash(f"No record found for PIN {pin}.", "error")
            return redirect(url_for("records"))
        session["form_purpose"] = "update_amendment"
        session["pin_input"] = pin
        session["editing_pin"] = pin
        name_parts = (member["member_name"] or "").split(" ")
        last_name = name_parts[-1] if len(name_parts) >= 1 else ""
        first_name = name_parts[0] if len(name_parts) >= 1 else ""
        middle_name = name_parts[1] if len(name_parts) >= 3 else ""
        suffix = name_parts[-1] if len(name_parts) >= 4 else ""
        mother_parts = (member["mother_fullname"] or "").split(", ")
        mother_last = mother_parts[0] if mother_parts else ""
        mother_first = mother_parts[1] if len(mother_parts) > 1 else ""
        spouse_parts = (member["spouse_fullname"] or "").split(", ")
        spouse_last = spouse_parts[0] if spouse_parts else ""
        spouse_first = spouse_parts[1] if len(spouse_parts) > 1 else ""
        session["p2_data"] = {
            "last_name": last_name,
            "first_name": first_name,
            "middle_name": middle_name,
            "suffix": suffix,
            "dob": str(member["date_of_birth"]) if member["date_of_birth"] else "",
            "place_of_birth": member["place_of_birth"] or "",
            "sex": "Male" if member["sex"] == "M" else "Female",
            "civil_status": member["civil_status"] or "",
            "citizenship": member["citizenship"] or "",
            "philsys_id": member["philsys_id"] or "",
            "mother_last_name": mother_last,
            "mother_first_name": mother_first,
            "spouse_last_name": spouse_last,
            "spouse_first_name": spouse_first,
        }
        session["p3_data"] = {
            "perm_street": member["permanent_address"] or "",
            "mail_street": member["mailing_address"] or member["permanent_address"] or "",
            "mobile": member["mobile_number"] or "",
            "home_phone": member["home_phone_number"] or "",
            "business_phone": member["business_line"] or "",
            "email": member["email_address"] or "",
            "same_as_perm": (member["mailing_address"] == member["permanent_address"]) or not member["mailing_address"]
        }
        cursor.execute("SELECT * FROM dependents WHERE fk_pin = %s", (pin,))
        deps = cursor.fetchall()
        session["p4_data"] = {"dependents": [{
            "name": d["dependents_full_name"],
            "relationship": d["relationship"],
            "dob": str(d["dependents_date_of_birth"]) if d["dependents_date_of_birth"] else "",
            "citizenship": d["dependents_citizenship"],
            "has_disability": d["dependent_has_disability"],
        } for d in deps]}
        session["p5_data"] = {
            "direct_profession": member["profession"] or "",
            "direct_monthly_income": str(member["monthly_income"]) if member["monthly_income"] else "",
            "member_type_status": member["fk_member_type"] or "",
            "pwd_id_no": member["pwd_id"] or "",
            "pra_srrv_no": member["srrv_id"] or "",
            "acr_icard_no": member["acr_id"] or "",
        }
        cursor.close()
        flash(f"Editing record for PIN {pin}. Update the fields below and submit.", "success")
        return redirect(url_for("page_2"))
    except Error as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect(url_for("records"))
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/')
def index():
    return render_template(
        'index.html',
        pin_input=session.get('pin_input', ''),
        form_purpose=session.get('form_purpose', '')
    )

@app.route('/submit_page_1', methods=['POST'])
def submit_page_1():
    session['form_purpose'] = request.form.get('form_purpose')
    session['pin_input'] = request.form.get('pin_input', '')
    return redirect(url_for('page_2'))

@app.route('/page_2')
def page_2():
    if 'form_purpose' not in session:
        return redirect(url_for('index'))
    return render_template('page2.html', data=session.get('p2_data', {}))

@app.route('/submit_page_2', methods=['POST'])
def submit_page_2():
    session['p2_data'] = request.form.to_dict()
    return redirect(url_for('page_3'))

@app.route('/page_3')
def page_3():
    if 'p2_data' not in session:
        return redirect(url_for('page_2'))
    return render_template('page_3.html', data=session.get('p3_data', {}))

@app.route('/submit_page_3', methods=['POST'])
def submit_page_3():
    p3_data = request.form.to_dict()
    if 'same_as_perm' in p3_data:
        p3_data['mail_unit'] = p3_data.get('perm_unit', '')
        p3_data['mail_lot'] = p3_data.get('perm_lot', '')
        p3_data['mail_street'] = p3_data.get('perm_street', '')
        p3_data['mail_subdivision'] = p3_data.get('perm_subdivision', '')
        p3_data['mail_barangay'] = p3_data.get('perm_barangay', '')
        p3_data['mail_city'] = p3_data.get('perm_city', '')
        p3_data['mail_province'] = p3_data.get('perm_province', '')
        p3_data['mail_zip'] = p3_data.get('perm_zip', '')
    session['p3_data'] = p3_data
    return redirect(url_for('page_4'))

@app.route('/page_4')
def page_4():
    if 'p3_data' not in session:
        return redirect(url_for('page_3'))
    return render_template('page4.html', data=session.get('p4_data', {}))

@app.route('/submit_page_4', methods=['POST'])
def submit_page_4():
    names = request.form.getlist('dep_name[]')
    relationships = request.form.getlist('dep_relationship[]')
    dobs = request.form.getlist('dep_dob[]')
    citizenships = request.form.getlist('dep_citizenship[]')
    disabilities = request.form.getlist('dep_disability[]')
    dependents_list = []
    for i in range(len(names)):
        has_dis = disabilities[i] if i < len(disabilities) else '0'
        dependents_list.append({
            "name": names[i],
            "relationship": relationships[i],
            "dob": dobs[i],
            "citizenship": citizenships[i],
            "has_disability": 1 if has_dis in [True, 1, '1', 'on', 'yes'] else 0
        })
    session['p4_data'] = {"dependents": dependents_list}
    return redirect(url_for('page_5'))

@app.route('/page_5')
def page_5():
    if 'p4_data' not in session:
        return redirect(url_for('page_4'))
    return render_template('page5.html', data=session.get('p5_data', {}))

@app.route('/submit_page_5', methods=['POST'])
def submit_page_5():
    p5_data = request.form.to_dict()
    p5_data['migrant_type_list'] = request.form.getlist('migrant_type')
    session['p5_data'] = p5_data
    return redirect(url_for('review'))

@app.route('/review')
def review():
    if 'p5_data' not in session:
        return redirect(url_for('page_5'))
    application_payload = {
        'purpose': {
            'form_purpose': session.get('form_purpose', 'new_registration'),
            'pin': session.get('pin_input', '')
        },
        'personal': session.get('p2_data', {}),
        'address': session.get('p3_data', {}),
        'dependents': session.get('p4_data', {}).get('dependents', []),
        'member_type': session.get('p5_data', {})
    }
    return render_template('review.html', data=application_payload)

@app.route('/submit_final', methods=['POST'])
def submit_final():
    if 'p5_data' not in session:
        return redirect(url_for('page_5'))
    p2 = session.get('p2_data', {})
    p3 = session.get('p3_data', {})
    p5 = session.get('p5_data', {})
    dependents = session.get('p4_data', {}).get('dependents', [])
    form_purpose = session.get('form_purpose', 'new_registration')
    is_update = form_purpose == 'update_amendment'
    perm_address = construct_address_string(p3, 'perm')
    mail_address = construct_address_string(p3, 'mail') or perm_address
    member_name = build_full_name(p2)
    mother_fullname = build_mother_fullname(p2)
    spouse_fullname = build_spouse_fullname(p2)
    sex = SEX_MAP.get(p2.get('sex'))
    civil_status = sanitize_field(p2.get('civil_status'))
    citizenship = CITIZENSHIP_MAP.get(p2.get('citizenship'))
    date_of_birth = sanitize_field(p2.get('dob'))
    place_of_birth = sanitize_field(p2.get('place_of_birth'), max_len=70)
    mobile_number = normalize_mobile(p3.get('mobile'))
    home_phone_number = sanitize_field(p3.get('home_phone'), max_len=30)
    business_line = sanitize_field(p3.get('business_phone'), max_len=50)
    email_address = sanitize_field(p3.get('email'), max_len=50)
    profession = sanitize_field(p5.get('direct_profession'), max_len=30)
    monthly_income = sanitize_field(p5.get('direct_monthly_income'), is_numeric=True)
    srrv_id = sanitize_field(p5.get('pra_srrv_no'), max_len=15)
    acr_id = sanitize_field(p5.get('acr_icard_no'), max_len=15)
    pwd_id = sanitize_field(p5.get('pwd_id_no'), max_len=20)
    fk_member_type = resolve_member_type(p5)
    pin = sanitize_field(session.get('pin_input'))
    editing_pin = session.get('editing_pin')
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if is_update:
            if not pin and editing_pin:
                pin = editing_pin
            elif not pin:
                cursor.close()
                conn.close()
                return "Error: A valid 12-digit PhilHealth PIN is required for updates/amendments.", 400
        else:
            if not pin:
                pin = generate_unique_pin(cursor)
                session['pin_input'] = pin
        required = {
            'Name': member_name,
            'Date of Birth': date_of_birth,
            'Place of Birth': place_of_birth,
            'Sex': sex,
            'Civil Status': civil_status,
            'Citizenship': citizenship,
            'Permanent Address': perm_address,
            'Mobile Number': mobile_number,
            'Email Address': email_address,
            "Mother's Name": mother_fullname,
            'Member Type': fk_member_type,
        }
        missing = [label for label, val in required.items() if not val]
        if missing:
            cursor.close()
            conn.close()
            return "Error: Missing or invalid required field(s): " + ", ".join(missing) + ". Please go back and complete them.", 400
        if is_update:
            update_query = """
                UPDATE members SET
                    member_name = %s, date_of_birth = %s, place_of_birth = %s,
                    sex = %s, civil_status = %s, citizenship = %s,
                    philsys_id = %s, permanent_address = %s, mailing_address = %s,
                    mobile_number = %s, home_phone_number = %s, business_line = %s,
                    email_address = %s, profession = %s, monthly_income = %s,
                    srrv_id = %s, acr_id = %s, pwd_id = %s,
                    mother_fullname = %s, spouse_fullname = %s, fk_member_type = %s
                WHERE pin = %s
            """
            update_values = (
                member_name, date_of_birth, place_of_birth,
                sex, civil_status, citizenship,
                sanitize_field(p2.get('philsys_id'), max_len=20),
                sanitize_field(perm_address),
                sanitize_field(mail_address),
                mobile_number, home_phone_number, business_line,
                email_address, profession, monthly_income,
                srrv_id, acr_id, pwd_id,
                mother_fullname, spouse_fullname, fk_member_type,
                pin
            )
            cursor.execute(update_query, update_values)
            cursor.execute("DELETE FROM dependents WHERE fk_pin = %s", (pin,))
        else:
            insert_query = """
                INSERT INTO members (
                    pin, member_name, date_of_birth, place_of_birth, sex, civil_status,
                    citizenship, philsys_id, permanent_address, mailing_address,
                    mobile_number, home_phone_number, business_line, email_address,
                    profession, monthly_income, srrv_id, acr_id, pwd_id,
                    mother_fullname, spouse_fullname, fk_member_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            insert_values = (
                pin, member_name, date_of_birth, place_of_birth, sex, civil_status,
                citizenship, sanitize_field(p2.get('philsys_id'), max_len=20),
                sanitize_field(perm_address), sanitize_field(mail_address),
                mobile_number, home_phone_number, business_line, email_address,
                profession, monthly_income, srrv_id, acr_id, pwd_id,
                mother_fullname, spouse_fullname, fk_member_type,
            )
            cursor.execute(insert_query, insert_values)
        for dep in dependents:
            dep_query = """
                INSERT INTO dependents (
                    dependents_full_name, relationship, dependents_date_of_birth,
                    dependents_citizenship, dependent_has_disability, fk_pin
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            dep_values = (
                sanitize_field(dep.get('name'), max_len=40),
                sanitize_field(dep.get('relationship'), max_len=15),
                sanitize_field(dep.get('dob')),
                sanitize_field(dep.get('citizenship'), max_len=15),
                dep.get('has_disability', 0),
                pin
            )
            cursor.execute(dep_query, dep_values)
        conn.commit()
        cursor.close()
        if is_update:
            session.pop('editing_pin', None)
    except Error as e:
        if conn:
            conn.rollback()
        return f"Database Transaction Error Occurred: {str(e)}", 500
    finally:
        if conn and conn.is_connected():
            conn.close()
    session['p2_data'] = {}
    session['p3_data'] = {}
    session['p4_data'] = {}
    session['p5_data'] = {}
    session['form_purpose'] = ''
    return redirect(url_for('success'))

@app.route('/success')
def success():
    if 'pin_input' not in session and 'p5_data' not in session:
        return redirect(url_for('index'))
    summary_dump = {
        "purpose_selection": {"purpose": session.get('form_purpose'), "pin": session.get('pin_input')},
        "step_1_personal": session.get('p2_data'),
        "step_2_address": session.get('p3_data'),
        "step_3_dependents": session.get('p4_data'),
        "step_4_member_type": session.get('p5_data')
    }
    pin = session.get('pin_input')
    session.clear()
    return f"""
    <div style="font-family: 'Inter', sans-serif; max-width: 650px; margin: 60px auto; padding: 32px; border: 1px solid #E2E8F0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;">
        <div style="width: 56px; height: 56px; background: #E8F5E9; color: #2E7D32; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; font-size: 24px; font-weight: bold;">✓</div>
        <h2 style="color: #003E7B; margin-bottom: 8px;">Registration Successfully Submitted</h2>
        <p style="color: #486581; font-size: 14px; margin-bottom: 24px;">Your multi-step PhilHealth Membership registration entry has been safely written to the database.</p>
        <div style="text-align: left;">
            <span style="font-size: 11px; font-weight: 700; color: #829AB1; text-transform: uppercase;">Parsed Submission Payload Matrix Log:</span>
            <pre style="background: #F0F4F8; padding: 16px; border-radius: 6px; overflow-x: auto; font-size: 12px; color: #102A43; border: 1px solid #D9E2EC; margin-top: 6px;">{summary_dump}</pre>
        </div>
        <div style="margin-top: 16px; display: flex; gap: 12px; justify-content: center;">
            <a href="/" style="display: inline-block; padding: 10px 20px; background: #003E7B; color: white; text-decoration: none; font-size: 13px; font-weight: 600; border-radius: 4px;">Register New Account</a>
            <a href="/records" style="display: inline-block; padding: 10px 20px; background: #74B72E; color: white; text-decoration: none; font-size: 13px; font-weight: 600; border-radius: 4px;">View All Records</a>
        </div>
        <div style="margin-top: 16px; font-size: 12px; color: #486581;">
            <strong>Your PIN:</strong> <span style="font-weight: 700; color: #003E7B;">{pin}</span>
        </div>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True)