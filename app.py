import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'supersecretkey_philhealth'

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "philhealth_db")
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def generate_pin():
    return ''.join(random.choices(string.digits, k=12))

def get_null_or_val(val):
    if not val:
        return None
    val = str(val).strip()
    return val if val else None

@app.route('/')
def index():
    return redirect(url_for('members'))

@app.route('/members', methods=['GET', 'POST'])
def members():
    conn = get_connection()
    if not conn:
        flash("Database connection error.", "error")
        return render_template('members.html', members=[], types=[])

    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        pin = generate_pin()
        inc = get_null_or_val(request.form.get('monthly_income'))
        if inc is not None:
            try:
                inc = int(inc)
                if inc <= 0:
                    flash("Monthly Income must be > 0", "error")
                    return redirect(url_for('members'))
            except ValueError:
                flash("Monthly Income must be a number", "error")
                return redirect(url_for('members'))

        sql = """
            INSERT INTO members (
                pin, member_name, date_of_birth, place_of_birth, sex, civil_status, citizenship, 
                permanent_address, mailing_address, mobile_number, home_phone_number, bussiness_line, 
                email_address, profession, monthly_income, philsys_id, srrv_id, acr_id, pwd_id, 
                mother_fullname, spouse_fullname, member_type
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        vals = (
            pin, request.form.get('member_name'), request.form.get('date_of_birth'),
            request.form.get('place_of_birth'), request.form.get('sex'),
            request.form.get('civil_status'), request.form.get('citizenship'),
            request.form.get('permanent_address'), get_null_or_val(request.form.get('mailing_address')),
            request.form.get('mobile_number'), get_null_or_val(request.form.get('home_phone_number')),
            get_null_or_val(request.form.get('bussiness_line')), request.form.get('email_address'),
            get_null_or_val(request.form.get('profession')), inc,
            get_null_or_val(request.form.get('philsys_id')), get_null_or_val(request.form.get('srrv_id')),
            get_null_or_val(request.form.get('acr_id')), get_null_or_val(request.form.get('pwd_id')),
            request.form.get('mother_fullname'), get_null_or_val(request.form.get('spouse_fullname')),
            request.form.get('member_type')
        )
        
        try:
            cursor.execute(sql, vals)
            conn.commit()
            flash(f"Member added successfully with PIN: {pin}", "success")
        except Error as e:
            flash(f"Database Error: {e}", "error")
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('members'))

    # GET request
    try:
        cursor.execute("SELECT * FROM members")
        members_list = cursor.fetchall()
        
        cursor.execute("SELECT member_type FROM contribution_type")
        types = [row['member_type'] for row in cursor.fetchall()]
    except Error as e:
        flash(f"Database Error: {e}", "error")
        members_list = []
        types = []
    finally:
        cursor.close()
        conn.close()

    return render_template('members.html', members=members_list, types=types)

@app.route('/members/<pin>', methods=['GET', 'POST'])
def member_detail(pin):
    conn = get_connection()
    if not conn:
        flash("Database connection error.", "error")
        return redirect(url_for('members'))

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        action = request.form.get('_method', '').upper()
        
        if action == 'DELETE':
            try:
                cursor.execute("DELETE FROM dependents WHERE pin = %s", (pin,))
                cursor.execute("DELETE FROM members WHERE pin = %s", (pin,))
                if cursor.rowcount > 0:
                    conn.commit()
                    flash("Member and their dependents deleted.", "success")
                else:
                    flash("Member not found.", "warning")
            except Error as e:
                conn.rollback()
                flash(f"Database Error: {e}", "error")
            finally:
                cursor.close()
                conn.close()
            return redirect(url_for('members'))
            
        else:
            # Update member
            inc = get_null_or_val(request.form.get('monthly_income'))
            if inc is not None:
                try:
                    inc = int(inc)
                    if inc <= 0:
                        flash("Monthly Income must be > 0", "error")
                        return redirect(url_for('member_detail', pin=pin))
                except ValueError:
                    flash("Monthly Income must be a number", "error")
                    return redirect(url_for('member_detail', pin=pin))

            sql = """
                UPDATE members SET 
                    member_name=%s, date_of_birth=%s, place_of_birth=%s, sex=%s, civil_status=%s, 
                    citizenship=%s, permanent_address=%s, mailing_address=%s, mobile_number=%s, 
                    home_phone_number=%s, bussiness_line=%s, email_address=%s, profession=%s, 
                    monthly_income=%s, philsys_id=%s, srrv_id=%s, acr_id=%s, pwd_id=%s, 
                    mother_fullname=%s, spouse_fullname=%s, member_type=%s
                WHERE pin=%s
            """
            vals = (
                request.form.get('member_name'), request.form.get('date_of_birth'), request.form.get('place_of_birth'),
                request.form.get('sex'), request.form.get('civil_status'), request.form.get('citizenship'),
                request.form.get('permanent_address'), get_null_or_val(request.form.get('mailing_address')),
                request.form.get('mobile_number'), get_null_or_val(request.form.get('home_phone_number')),
                get_null_or_val(request.form.get('bussiness_line')), request.form.get('email_address'),
                get_null_or_val(request.form.get('profession')), inc,
                get_null_or_val(request.form.get('philsys_id')), get_null_or_val(request.form.get('srrv_id')),
                get_null_or_val(request.form.get('acr_id')), get_null_or_val(request.form.get('pwd_id')),
                request.form.get('mother_fullname'), get_null_or_val(request.form.get('spouse_fullname')),
                request.form.get('member_type'), pin
            )
            
            try:
                cursor.execute(sql, vals)
                conn.commit()
                flash("Member updated successfully.", "success")
            except Error as e:
                flash(f"Database Error: {e}", "error")
            finally:
                cursor.close()
                conn.close()
                
            return redirect(url_for('member_detail', pin=pin))

    # GET request for viewing/editing a member
    try:
        cursor.execute("SELECT * FROM members WHERE pin = %s", (pin,))
        member = cursor.fetchone()
        
        cursor.execute("SELECT member_type FROM contribution_type")
        types = [row['member_type'] for row in cursor.fetchall()]
    except Error as e:
        flash(f"Database Error: {e}", "error")
        member = None
        types = []
    finally:
        cursor.close()
        conn.close()

    if not member:
        flash("Member not found.", "error")
        return redirect(url_for('members'))

    return render_template('member_detail.html', member=member, types=types)


@app.route('/dependents', methods=['GET', 'POST'])
def dependents():
    conn = get_connection()
    if not conn:
        flash("Database connection error.", "error")
        return render_template('dependents.html', dependents=[])

    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        pin = request.form.get('pin')
        if not pin:
            flash("Member PIN is required.", "error")
            return redirect(url_for('dependents'))
            
        cursor.execute("SELECT pin FROM members WHERE pin = %s", (pin,))
        if not cursor.fetchone():
            flash("Member not found for that PIN.", "error")
            return redirect(url_for('dependents'))
            
        dis = get_null_or_val(request.form.get('dependent_has_disability'))
        if dis is not None:
            dis = int(dis)
            
        sql = """
            INSERT INTO dependents (dependents_full_name, relationship, dependents_date_of_birth, 
            dependents_citizenship, dependent_has_disability, pin)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        vals = (
            request.form.get('dependents_full_name'), request.form.get('relationship'),
            request.form.get('dependents_date_of_birth'), request.form.get('dependents_citizenship'),
            dis, pin
        )
        
        try:
            cursor.execute(sql, vals)
            conn.commit()
            flash("Dependent added successfully.", "success")
        except Error as e:
            flash(f"Database Error: {e}", "error")
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('dependents'))

    # GET request
    try:
        cursor.execute("SELECT * FROM dependents")
        deps = cursor.fetchall()
    except Error as e:
        flash(f"Database Error: {e}", "error")
        deps = []
    finally:
        cursor.close()
        conn.close()

    return render_template('dependents.html', dependents=deps)

@app.route('/dependents/<int:dependents_id>', methods=['POST', 'DELETE'])
def delete_dependent(dependents_id):
    # Support both true DELETE method (if using fetch API) or POST with _method=DELETE
    action = request.form.get('_method', '').upper()
    if request.method == 'DELETE' or action == 'DELETE':
        conn = get_connection()
        if not conn:
            flash("Database connection error.", "error")
            return redirect(url_for('dependents'))
            
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM dependents WHERE dependents_id = %s", (dependents_id,))
            if cursor.rowcount > 0:
                conn.commit()
                flash("Dependent deleted.", "success")
            else:
                flash("Dependent not found.", "warning")
        except Error as e:
            flash(f"Database Error: {e}", "error")
        finally:
            cursor.close()
            conn.close()
            
    return redirect(url_for('dependents'))

@app.route('/member-types', methods=['GET'])
def get_member_types():
    conn = get_connection()
    if not conn:
        return {"error": "Database connection error"}, 500
        
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT member_type, contribution_type FROM contribution_type")
        types = cursor.fetchall()
        return {"types": types}
    except Error as e:
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
