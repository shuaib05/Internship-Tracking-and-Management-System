import os
import pymysql
from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, flash

# Configure to serve the frontend folder
frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(
    __name__,
    template_folder=frontend_folder,
    static_folder=frontend_folder,
    static_url_path=''
)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_change_me')

# Configure MySQL Database Connection
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'itms_db')

def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') != role:
                flash('You do not have permission to access that page.', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def roles_accepted(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('You do not have permission to access that page.', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def home():
    """Redirect to login page."""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
                user = cursor.fetchone()
            conn.close()
            
            # Simple plaintext password check mapping to sample data
            if user and user['Password'] == password:
                session.clear()
                session['user_id'] = user['UserID']
                session['role'] = user['Role']
                session['ref_id'] = user['RefID']
                session['username'] = user['Username']
                
                if user['Role'] == 'student':
                    return redirect(url_for('student_dashboard'))
                elif user['Role'] == 'faculty':
                    return redirect(url_for('faculty_dashboard'))
                elif user['Role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password', 'error')
        except Exception as e:
            flash(f'Database error: {str(e)}', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/student/dashboard')
@role_required('student')
def student_dashboard():
    student_id = session.get('ref_id')
    application_count = 0
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM Application WHERE StudentID = %s", (student_id,))
            result = cursor.fetchone()
            if result:
                application_count = result['count']
        conn.close()
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        
    return render_template('student_dashboard.html', application_count=application_count)

@app.route('/student/profile', methods=['GET', 'POST'])
@role_required('student')
def student_profile():
    student_id = session.get('ref_id')
    try:
        conn = get_db_connection()
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Student SET Name = %s, Email = %s, Phone = %s 
                    WHERE StudentID = %s
                """, (name, email, phone, student_id))
            conn.commit()
            flash('Profile updated successfully!', 'success')
            
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Student WHERE StudentID = %s", (student_id,))
            student = cursor.fetchone()
        conn.close()
        return render_template('student_profile.html', student=student)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('student_dashboard'))

@app.route('/student/internships')
@role_required('student')
def student_internships():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT i.*, c.CompanyName 
                FROM Internship i 
                JOIN Company c ON i.CompanyID = c.CompanyID
            """)
            internships = cursor.fetchall()
        conn.close()
        return render_template('student_internships.html', internships=internships)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('student_dashboard'))

@app.route('/student/apply/<int:internship_id>', methods=['POST'])
@role_required('student')
def student_apply(internship_id):
    student_id = session.get('ref_id')
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check for duplicates
            cursor.execute("""
                SELECT * FROM Application 
                WHERE StudentID = %s AND InternshipID = %s
            """, (student_id, internship_id))
            existing = cursor.fetchone()
            
            if existing:
                flash('You have already applied for this internship!', 'warning')
            else:
                cursor.execute("""
                    INSERT INTO Application (DateApplied, Status, StudentID, InternshipID) 
                    VALUES (CURDATE(), 'Pending', %s, %s)
                """, (student_id, internship_id))
                conn.commit()
                flash('Application submitted successfully!', 'success')
        conn.close()
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
    
    return redirect(url_for('student_internships'))

@app.route('/student/applications')
@role_required('student')
def student_applications():
    student_id = session.get('ref_id')
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT a.DateApplied, a.Status, i.Title, c.CompanyName 
                FROM Application a 
                JOIN Internship i ON a.InternshipID = i.InternshipID 
                JOIN Company c ON i.CompanyID = c.CompanyID 
                WHERE a.StudentID = %s
                ORDER BY a.DateApplied DESC
            """, (student_id,))
            applications = cursor.fetchall()
        conn.close()
        return render_template('student_applications.html', applications=applications)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('student_dashboard'))

@app.route('/faculty/dashboard')
@role_required('faculty')
def faculty_dashboard():
    faculty_id = session.get('ref_id')
    stats = {'internships': 0, 'applications': 0}
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as c FROM Internship WHERE FacultyID = %s", (faculty_id,))
            stats['internships'] = cursor.fetchone()['c']
            
            cursor.execute("""
                SELECT COUNT(a.ApplicationID) as c 
                FROM Application a 
                JOIN Internship i ON a.InternshipID = i.InternshipID 
                WHERE i.FacultyID = %s
            """, (faculty_id,))
            stats['applications'] = cursor.fetchone()['c']
        conn.close()
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
    return render_template('faculty_dashboard.html', stats=stats)

@app.route('/faculty/applications')
@role_required('faculty')
def faculty_applications():
    faculty_id = session.get('ref_id')
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT a.DateApplied, a.Status, s.Name, d.DepartmentName, i.Title 
                FROM Application a 
                JOIN Student s ON a.StudentID = s.StudentID 
                LEFT JOIN Department d ON s.DepartmentID = d.DepartmentID 
                JOIN Internship i ON a.InternshipID = i.InternshipID 
                WHERE i.FacultyID = %s
                ORDER BY a.DateApplied DESC
            """, (faculty_id,))
            applications = cursor.fetchall()
        conn.close()
        return render_template('faculty_applications.html', applications=applications)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('faculty_dashboard'))

@app.route('/faculty/internships')
@role_required('faculty')
def faculty_internships():
    faculty_id = session.get('ref_id')
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT i.Title, i.Duration, i.Stipend, c.CompanyName, 
                       (SELECT COUNT(*) FROM Application a WHERE a.InternshipID = i.InternshipID) as ApplicantCount
                FROM Internship i 
                JOIN Company c ON i.CompanyID = c.CompanyID
                WHERE i.FacultyID = %s
            """, (faculty_id,))
            internships = cursor.fetchall()
        conn.close()
        return render_template('faculty_internships.html', internships=internships)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('faculty_dashboard'))

@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    stats = {'students': 0, 'internships': 0, 'applications': 0, 'pending': 0}
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as c FROM Student")
            stats['students'] = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM Internship")
            stats['internships'] = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM Application")
            stats['applications'] = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM Application WHERE Status = 'Pending'")
            stats['pending'] = cursor.fetchone()['c']
        conn.close()
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/admin/companies', methods=['GET', 'POST'])
@role_required('admin')
def admin_companies():
    try:
        conn = get_db_connection()
        if request.method == 'POST':
            name = request.form.get('company_name')
            email = request.form.get('contact_email')
            location = request.form.get('location')
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Company (CompanyName, ContactEmail, Location) 
                    VALUES (%s, %s, %s)
                """, (name, email, location))
            conn.commit()
            flash('Company added successfully!', 'success')
            return redirect(url_for('admin_companies'))

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Company")
            companies = cursor.fetchall()
        conn.close()
        return render_template('admin_companies.html', companies=companies)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/companies/edit/<int:id>', methods=['GET', 'POST'])
@role_required('admin')
def admin_company_edit(id):
    try:
        conn = get_db_connection()
        if request.method == 'POST':
            name = request.form.get('company_name')
            email = request.form.get('contact_email')
            location = request.form.get('location')
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Company SET CompanyName=%s, ContactEmail=%s, Location=%s 
                    WHERE CompanyID=%s
                """, (name, email, location, id))
            conn.commit()
            flash('Company updated successfully!', 'success')
            return redirect(url_for('admin_companies'))
            
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Company WHERE CompanyID=%s", (id,))
            company = cursor.fetchone()
        conn.close()
        if not company:
            flash('Company not found', 'error')
            return redirect(url_for('admin_companies'))
        return render_template('admin_company_edit.html', company=company)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('admin_companies'))

@app.route('/admin/companies/delete/<int:id>', methods=['POST'])
@role_required('admin')
def admin_company_delete(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Company WHERE CompanyID=%s", (id,))
        conn.commit()
        conn.close()
        flash('Company deleted successfully!', 'success')
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
    return redirect(url_for('admin_companies'))

@app.route('/admin/internships', methods=['GET', 'POST'])
@role_required('admin')
def admin_internships():
    try:
        conn = get_db_connection()
        if request.method == 'POST':
            title = request.form.get('title')
            duration = request.form.get('duration')
            stipend = request.form.get('stipend')
            company_id = request.form.get('company_id')
            faculty_id = request.form.get('faculty_id')
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Internship (Title, Duration, Stipend, CompanyID, FacultyID) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (title, duration, stipend, company_id, faculty_id))
            conn.commit()
            flash('Internship added successfully!', 'success')
            return redirect(url_for('admin_internships'))

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT i.*, c.CompanyName, f.FacultyName 
                FROM Internship i 
                LEFT JOIN Company c ON i.CompanyID = c.CompanyID
                LEFT JOIN Faculty f ON i.FacultyID = f.FacultyID
            """)
            internships = cursor.fetchall()
            
            cursor.execute("SELECT * FROM Company")
            companies = cursor.fetchall()
            cursor.execute("SELECT * FROM Faculty")
            faculties = cursor.fetchall()
        conn.close()
        return render_template('admin_internships.html', internships=internships, companies=companies, faculties=faculties)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/internships/edit/<int:id>', methods=['GET', 'POST'])
@role_required('admin')
def admin_internship_edit(id):
    try:
        conn = get_db_connection()
        if request.method == 'POST':
            title = request.form.get('title')
            duration = request.form.get('duration')
            stipend = request.form.get('stipend')
            company_id = request.form.get('company_id')
            faculty_id = request.form.get('faculty_id')
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Internship SET Title=%s, Duration=%s, Stipend=%s, CompanyID=%s, FacultyID=%s 
                    WHERE InternshipID=%s
                """, (title, duration, stipend, company_id, faculty_id, id))
            conn.commit()
            flash('Internship updated successfully!', 'success')
            return redirect(url_for('admin_internships'))
            
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Internship WHERE InternshipID=%s", (id,))
            internship = cursor.fetchone()
            cursor.execute("SELECT * FROM Company")
            companies = cursor.fetchall()
            cursor.execute("SELECT * FROM Faculty")
            faculties = cursor.fetchall()
        conn.close()
        return render_template('admin_internship_edit.html', internship=internship, companies=companies, faculties=faculties)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('admin_internships'))

@app.route('/admin/internships/delete/<int:id>', methods=['POST'])
@role_required('admin')
def admin_internship_delete(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Internship WHERE InternshipID=%s", (id,))
        conn.commit()
        conn.close()
        flash('Internship deleted successfully!', 'success')
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
    return redirect(url_for('admin_internships'))

@app.route('/admin/students', methods=['GET', 'POST'])
@role_required('admin')
def admin_students():
    try:
        conn = get_db_connection()
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            department_id = request.form.get('department_id')
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Student (Name, Email, Phone, DepartmentID)
                    VALUES (%s, %s, %s, %s)
                """, (name, email, phone, department_id))
                student_id = cursor.lastrowid
                
                # Default username: firstname_firstletteroflastname all lowercase
                name_parts = name.strip().split()
                if len(name_parts) >= 2:
                    username = f"{name_parts[0].lower()}_{name_parts[-1][0].lower()}"
                else:
                    username = name_parts[0].lower()
                cursor.execute("""
                    INSERT INTO Users (Username, Password, Role, RefID)
                    VALUES (%s, 'password', 'student', %s)
                """, (username, student_id))
            conn.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('admin_students'))

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.*, d.DepartmentName 
                FROM Student s 
                LEFT JOIN Department d ON s.DepartmentID = d.DepartmentID
            """)
            students = cursor.fetchall()
            cursor.execute("SELECT * FROM Department")
            departments = cursor.fetchall()
        conn.close()
        return render_template('admin_students.html', students=students, departments=departments)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/students/edit/<int:id>', methods=['GET', 'POST'])
@role_required('admin')
def admin_student_edit(id):
    try:
        conn = get_db_connection()
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            department_id = request.form.get('department_id')
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Student SET Name=%s, Email=%s, Phone=%s, DepartmentID=%s 
                    WHERE StudentID=%s
                """, (name, email, phone, department_id, id))
            conn.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('admin_students'))
            
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Student WHERE StudentID=%s", (id,))
            student = cursor.fetchone()
            cursor.execute("SELECT * FROM Department")
            departments = cursor.fetchall()
        conn.close()
        if not student:
            flash('Student not found', 'error')
            return redirect(url_for('admin_students'))
        return render_template('admin_student_edit.html', student=student, departments=departments)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('admin_students'))

@app.route('/admin/students/delete/<int:id>', methods=['POST'])
@role_required('admin')
def admin_student_delete(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Users WHERE Role='student' AND RefID=%s", (id,))
            cursor.execute("DELETE FROM Student WHERE StudentID=%s", (id,))
        conn.commit()
        conn.close()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
    return redirect(url_for('admin_students'))

@app.route('/admin/faculty', methods=['GET', 'POST'])
@role_required('admin')
def admin_faculty():
    try:
        conn = get_db_connection()
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Faculty (FacultyName, FacultyEmail)
                    VALUES (%s, %s)
                """, (name, email))
                faculty_id = cursor.lastrowid
                
                # Default username: firstname_firstletteroflastname all lowercase
                name_parts = name.strip().split()
                if len(name_parts) >= 2:
                    username = f"{name_parts[0].lower()}_{name_parts[-1][0].lower()}"
                else:
                    username = name_parts[0].lower()
                cursor.execute("""
                    INSERT INTO Users (Username, Password, Role, RefID)
                    VALUES (%s, 'password', 'faculty', %s)
                """, (username, faculty_id))
            conn.commit()
            flash('Faculty added successfully!', 'success')
            return redirect(url_for('admin_faculty'))

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Faculty")
            faculty = cursor.fetchall()
        conn.close()
        return render_template('admin_faculty.html', faculty=faculty)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/faculty/edit/<int:id>', methods=['GET', 'POST'])
@role_required('admin')
def admin_faculty_edit(id):
    try:
        conn = get_db_connection()
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Faculty SET FacultyName=%s, FacultyEmail=%s 
                    WHERE FacultyID=%s
                """, (name, email, id))
            conn.commit()
            flash('Faculty updated successfully!', 'success')
            return redirect(url_for('admin_faculty'))
            
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Faculty WHERE FacultyID=%s", (id,))
            faculty = cursor.fetchone()
        conn.close()
        if not faculty:
            flash('Faculty not found', 'error')
            return redirect(url_for('admin_faculty'))
        return render_template('admin_faculty_edit.html', faculty=faculty)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('admin_faculty'))

@app.route('/admin/faculty/delete/<int:id>', methods=['POST'])
@role_required('admin')
def admin_faculty_delete(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Users WHERE Role='faculty' AND RefID=%s", (id,))
            cursor.execute("DELETE FROM Faculty WHERE FacultyID=%s", (id,))
        conn.commit()
        conn.close()
        flash('Faculty deleted successfully!', 'success')
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
    return redirect(url_for('admin_faculty'))

@app.route('/admin/applications')
@role_required('admin')
def admin_applications():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT a.*, s.Name, i.Title 
                FROM Application a 
                JOIN Student s ON a.StudentID = s.StudentID 
                JOIN Internship i ON a.InternshipID = i.InternshipID
                ORDER BY a.DateApplied DESC
            """)
            applications = cursor.fetchall()
        conn.close()
        return render_template('admin_applications.html', applications=applications)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/applications/update/<int:id>', methods=['POST'])
@role_required('admin')
def admin_application_update(id):
    try:
        status = request.form.get('status')
        if status in ['Pending', 'Accepted', 'Rejected']:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("UPDATE Application SET Status=%s WHERE ApplicationID=%s", (status, id))
            conn.commit()
            conn.close()
            flash('Application status updated!', 'success')
        else:
            flash('Invalid status selected.', 'error')
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
    return redirect(url_for('admin_applications'))

@app.route('/reports')
@roles_accepted('admin', 'faculty')
def reports():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 1. Applications by Department
            cursor.execute("""
                SELECT d.DepartmentName, COUNT(a.ApplicationID) as count 
                FROM Department d 
                LEFT JOIN Student s ON d.DepartmentID = s.DepartmentID 
                LEFT JOIN Application a ON s.StudentID = a.StudentID 
                GROUP BY d.DepartmentID, d.DepartmentName
                ORDER BY count DESC
            """)
            apps_by_dept = cursor.fetchall()
            
            # 2. Applications by Company
            cursor.execute("""
                SELECT c.CompanyName, COUNT(a.ApplicationID) as count 
                FROM Company c 
                LEFT JOIN Internship i ON c.CompanyID = i.CompanyID 
                LEFT JOIN Application a ON i.InternshipID = a.InternshipID 
                GROUP BY c.CompanyID, c.CompanyName
                ORDER BY count DESC
            """)
            apps_by_company = cursor.fetchall()
            
            # 3. Acceptance rate
            cursor.execute("SELECT COUNT(*) as c FROM Application")
            total_apps = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM Application WHERE Status = 'Accepted'")
            accepted_apps = cursor.fetchone()['c']
            
            acceptance_rate = 0
            if total_apps > 0:
                acceptance_rate = round((accepted_apps / total_apps) * 100, 2)
                
            # 4. Top 5 Internships
            cursor.execute("""
                SELECT i.Title, c.CompanyName, COUNT(a.ApplicationID) as count 
                FROM Internship i 
                JOIN Company c ON i.CompanyID = c.CompanyID 
                LEFT JOIN Application a ON i.InternshipID = a.InternshipID 
                GROUP BY i.InternshipID, i.Title, c.CompanyName
                ORDER BY count DESC
                LIMIT 5
            """)
            top_internships = cursor.fetchall()
        conn.close()
        
        return render_template('reports.html', 
                               apps_by_dept=apps_by_dept,
                               apps_by_company=apps_by_company,
                               acceptance_rate=acceptance_rate,
                               total_apps=total_apps,
                               top_internships=top_internships)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    # Start the Flask development server on port 5000
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
