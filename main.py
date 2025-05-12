import mysql.connector
import csv
from datetime import datetime, timedelta

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

SUBJECT_SCHEDULE = {
    0: [('ADA', 1), ('DMS', 2), ('BIOLOGY', 3), ('BIOLOGY', 4)],     # Monday
    1: [('MC', 1), ('PHC', 2), ('ADA', 3), ('UHV', 4)],             # Tuesday
    2: [('DBMS', 1), ('PHC', 2), ('ADA', 3), ('DMS', 4)],           # Wednesday
    3: [('MC', 1), ('ADA', 2), ('PHC', 3), ('DBMS', 4)],            # Thursday
    4: [('BIOLOGY', 1), ('PHC', 2), ('DMS', 3), ('MC', 4)],         # Friday
    5: [('DBMS', 1), ('DBMS', 2), ('DBMS', 3), ('DBMS', 4)],        # Saturday
}

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="leave"
    )

def login(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return 'admin'
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()
    return 'student' if user else None

def student_menu(usn):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT `FROM`, `TO`, STATUS FROM permission WHERE USN = %s AND NOTIFIED = FALSE AND STATUS != 'pending'", (usn,))
    for f, t, status in cursor.fetchall():
        print(f"\n📢 Notification: Your leave request from {f} to {t} has been {status}.")
    cursor.execute("UPDATE permission SET NOTIFIED = TRUE WHERE USN = %s AND STATUS != 'pending'", (usn,))
    conn.commit()

    while True:
        print(f"\nWelcome, Student {usn}")
        print("1. Apply for Leave")
        print("2. View Subject Leaves")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            apply_leave(usn)
        elif choice == "2":
            check_subject_leaves(usn)
        elif choice == "3":
            break
        else:
            print("Invalid choice.")

def apply_leave(usn, name=None, from_date=None, to_date=None, reason=None):
    if not name:
        name = input("Enter your name: ")
        from_date = input("From Date (YYYY-MM-DD): ")
        to_date = input("To Date (YYYY-MM-DD): ")
        reason = input("Enter the reason for leave: ")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO permission (USN, NAME, `LEAVE`, `FROM`, `TO`, STATUS, REASON) VALUES (%s, %s, 'yes', %s, %s, 'pending', %s)",
        (usn, name, from_date, to_date, reason)
    )
    conn.commit()
    conn.close()
    if not name:
        print("Leave request submitted successfully.")

def check_subject_leaves(usn, gui=False):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject, COUNT(*) 
        FROM subject_leaves 
        WHERE USN = %s 
        GROUP BY subject
    """, (usn,))
    
    records = cursor.fetchall()
    conn.close()

    if not records:
        result = "No subject leaves found."
    else:
        result = "\n".join([f"{subj}: {count} leaves" for subj, count in records])

    if gui:
        return result
    else:
        print(result)

def update_subject_tables(usn, from_date_str, to_date_str):
    conn = get_connection()
    cursor = conn.cursor()

    from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d")

    while from_date <= to_date:
        day = from_date.weekday()
        schedule = SUBJECT_SCHEDULE.get(day, [])
        for subject, period in schedule:
            cursor.execute("""
                INSERT INTO subject_leaves (USN, subject, date, period)
                VALUES (%s, %s, %s, %s)
            """, (usn, subject, from_date.date(), period))
            print(f"Marked leave for {subject} on {from_date.date()} (Period {period})")
        from_date += timedelta(days=1)

    conn.commit()
    conn.close()

def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. View Pending Leave Requests")
        print("2. View All Leave Records")
        print("3. Export All Attendance Data (CSV)")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM permission WHERE STATUS = 'pending'")
            requests = cursor.fetchall()

            if not requests:
                print("No pending leave requests.")
                conn.close()
                continue

            for row in requests:
                print(f"\nUSN: {row[0]}, Name: {row[1]}, From: {row[3]}, To: {row[4]}, Reason: {row[6]}, Status: {row[5]}")
                decision = input("Approve (a) / Reject (r) / Skip (s): ").lower()
                if decision in ['a', 'r']:
                    status = 'Approved' if decision == 'a' else 'Rejected'

                    cursor.execute("""
                        UPDATE permission
                        SET STATUS = %s
                        WHERE USN = %s AND `FROM` = %s AND `TO` = %s AND STATUS = 'pending'
                    """, (status, row[0], row[3], row[4]))
                    conn.commit()

                    print(f"Leave {status.lower()}.")

                    if status == 'Approved':
                        try:
                            update_subject_tables(row[0], row[3].strftime("%Y-%m-%d"), row[4].strftime("%Y-%m-%d"))
                        except Exception as e:
                            print(f"⚠️ Error updating subject leaves: {e}")

            conn.close()

        elif choice == "2":
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM permission")
            for row in cursor.fetchall():
                print(row)
            conn.close()

        elif choice == "3":
            export_all_attendance_to_csv()

        elif choice == "4":
            print("Exiting admin panel.")
            break

        else:
            print("Invalid choice.")

def export_all_attendance_to_csv():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subject_leaves")
    data = cursor.fetchall()

    with open("attendance_report.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["USN", "Subject", "Date", "Period"])
        writer.writerows(data)

    conn.close()
    print("📂 Attendance data exported to 'attendance_report.csv'")

def main():
    print("=== Login ===")
    username = input("Username: ")
    password = input("Password: ")
    role = login(username, password)
    if role == 'admin':
        admin_menu()
    elif role == 'student':
        student_menu(username)
    else:
        print("Invalid credentials.")

if __name__ == "__main__":
    main()
