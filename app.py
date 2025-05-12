from flask import Flask, render_template, request, redirect, session, flash
import main

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = main.login(username, password)

        if role == 'admin':
            session['user'] = username
            session['role'] = 'admin'  
            return redirect('/admin')
        elif role == 'student':
            session['user'] = username
            session['role'] = 'student' 
            return redirect('/student')
        else:
            flash("Invalid credentials.")
            return redirect('/')
    return render_template('login.html')


@app.route('/student')
def student_dashboard():
    usn = session.get('user')
    if not usn:
        return redirect('/')
    conn = main.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT `FROM`, `TO`, STATUS FROM permission WHERE USN = %s AND NOTIFIED = FALSE AND STATUS != 'pending'", (usn,))
    notifications = cursor.fetchall()
    cursor.execute("UPDATE permission SET NOTIFIED = TRUE WHERE USN = %s AND STATUS != 'pending'", (usn,))
    conn.commit()
    conn.close()
    return render_template('student_dashboard.html', usn=usn, notifications=notifications)

@app.route('/subject_leaves')
def subject_leaves():
    usn = session.get('user')
    if not usn:
        return redirect('/')
    leaves_output = main.check_subject_leaves(usn, gui=True)
    return render_template('student_subject_leaves.html', leaves=leaves_output.split('\n'))

@app.route('/student/leaves')
def student_subject_leaves():
    usn = session.get('user')
    if not usn:
        return redirect('/')
    leaves = main.check_subject_leaves(usn, gui=True)
    return render_template('student_leaves.html', leaves=leaves.split('\n'))

@app.route('/student/apply', methods=['GET', 'POST'])
def apply_leave():
    usn = session.get('user')
    if not usn:
        return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        reason = request.form['reason']
        main.apply_leave(usn, name, from_date, to_date, reason)
        flash("Leave request submitted.")
        return redirect('/student')
    return render_template('student_apply_leave.html')


@app.route('/student/status')
def view_status():
    usn = session.get('user')
    if not usn:
        return redirect('/')
    conn = main.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT `FROM`, `TO`, STATUS FROM permission WHERE USN = %s", (usn,))
    leaves = cursor.fetchall()
    conn.close()
    return render_template("student_leave_status.html", leaves=leaves)


@app.route('/admin')
def admin_dashboard():
    if session.get('user') != 'admin':
        return redirect('/')
    return render_template('admin_dashboard.html')

@app.route('/admin/records')
def admin_records():
    if session.get('user') != 'admin':
        return redirect('/')
    
    # Get filter parameters from request
    usn = request.args.get('usn', '').strip().upper()
    name = request.args.get('name', '').strip()
    status = request.args.get('status', '').strip()
    from_date = request.args.get('from_date', '').strip()
    to_date = request.args.get('to_date', '').strip()
    
    conn = main.get_connection()
    cursor = conn.cursor()
    
    # Base query
    query = "SELECT USN, NAME, `FROM`, `TO`, REASON, STATUS, NOTIFIED FROM permission WHERE 1=1"
    params = []
    
    # Add filters
    if usn:
        query += " AND USN LIKE %s"
        params.append(f"%{usn}%")
    if name:
        query += " AND NAME LIKE %s"
        params.append(f"%{name}%")
    if status:
        query += " AND STATUS = %s"
        params.append(status)
    if from_date:
        query += " AND `FROM` >= %s"
        params.append(from_date)
    if to_date:
        query += " AND `TO` <= %s"
        params.append(to_date)
    
    # Execute query
    cursor.execute(query, params)
    records = cursor.fetchall()
    conn.close()
    
    return render_template("admin_records.html", records=records)

@app.route('/admin/export')
def admin_export():
    if session.get('user') != 'admin':
        return redirect('/')
    main.export_all_attendance_to_csv()
    flash("📂 Attendance exported to attendance_report.csv")
    return redirect('/admin')

@app.route('/admin/requests', methods=['GET', 'POST'])
def admin_leave_requests():
    if session.get('user') != 'admin':
        return redirect('/')

    conn = main.get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        usn = request.form['usn']
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        decision = request.form['decision']
        status = 'Approved' if decision == 'approve' else 'Rejected'

        cursor.execute("""
            UPDATE permission SET STATUS = %s
            WHERE USN = %s AND `FROM` = %s AND `TO` = %s AND STATUS = 'pending'
        """, (status, usn, from_date, to_date))
        conn.commit()

        if status == 'Approved':
            main.update_subject_tables(usn, from_date, to_date)

        print(f"[INFO] {usn}'s request {status.lower()}")

    cursor.execute("SELECT USN, NAME, `FROM`, `TO`, REASON FROM permission WHERE STATUS = 'pending'")
    requests = cursor.fetchall()
    conn.close()
    return render_template("admin_leave_requests.html", requests=requests)

if __name__ == '__main__':
    app.run(debug=True)
