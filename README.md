# 📝 Leave Management System (Flask + MySQL)

A web-based leave management application designed for students and administrators.

## 🚀 Features

- Student login with USN
- Apply for leaves with date and reason
- Admin panel to view, approve, and reject leave requests
- Student notification dashboard for approvals/rejections
- Subject-wise leave tracking
- Export all attendance records to CSV

---

## 🧱 Tech Stack

- Python (Flask)
- MySQL
- HTML (Jinja2 Templates)
- Bootstrap (via ttkbootstrap or custom styling)
  
---


### **1. Clone the Repository**

```bash
git clone https://github.com/YOUR_USERNAME/leave-management-system.git
cd leave-management-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Create and Configure the Database

#Import the SQL structure into MySQL:
```bash
mysql -u root -p < database.sql
```
> Replace root with your MySQL username if different. You’ll be prompted for your MySQL password.



### 4. Run the Application
```bash
python app.py
```
Visit: http://127.0.0.1:5000 in your browser
