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

@app.route('/')
def home():
    """Serve the homepage."""
    return render_template('index.html')

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
    return render_template('student_dashboard.html')

@app.route('/faculty/dashboard')
@role_required('faculty')
def faculty_dashboard():
    return render_template('faculty_dashboard.html')

@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    # Start the Flask development server on port 5000
    app.run(debug=True, port=5000)
