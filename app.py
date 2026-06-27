from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_moment import Moment
import bcrypt
import MySQLdb.cursors
from datetime import datetime, date, timedelta
import os
import mysql.connector as mysql_connector
from mysql.connector import Error

app = Flask(__name__)

# Session configuration
app.secret_key = 'your_secret_key_here_change_in_production'

# Initialize Flask-Moment for date/time formatting in templates
moment = Moment(app)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'gietu'
app.config['MYSQL_DB'] = 'mess_management'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_AUTOCOMMIT'] = True

# Initialize Flask-MySQLdb (keep for compatibility)
mysql = MySQL(app)

# Database connection pool for reliable connections
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'gietu',
    'database': 'mess_management'
}

# Helper function to get database cursor reliably
def get_db_connection():
    """Get a direct database connection using mysql.connector"""
    try:
        conn = mysql_connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise Exception(f"MySQL Connection Error: {str(e)}")

# Global connection storage for the duration of a request
_db_connection = None

def get_db_cursor():
    """Get a database cursor reliably - stores connection for cleanup"""
    global _db_connection
    try:
        _db_connection = get_db_connection()
        cursor = _db_connection.cursor(dictionary=True)
        return cursor
    except Error as e:
        raise Exception(f"Database Cursor Error: {str(e)}")

def close_db_connection():
    """Close the database connection"""
    global _db_connection
    if _db_connection and _db_connection.is_connected():
        _db_connection.close()
        _db_connection = None

# commit helper uses the same connection created by get_db_cursor
def commit_db():
    """Commit the current database connection if available"""
    global _db_connection
    if _db_connection and _db_connection.is_connected():
        try:
            _db_connection.commit()
        except Exception as e:
            print(f"Commit error: {e}")


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute a database query safely"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
            return result
        elif fetch_all:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Database Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Helper functions
def is_admin_logged_in():
    return 'admin_id' in session

def is_student_logged_in():
    return 'student_id' in session

# Teardown function to close database connection after each request
@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection at the end of each request"""
    close_db_connection()

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            flash('Please login as admin to access this page', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_student_logged_in():
            flash('Please login as student to access this page', 'danger')
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-db')
def test_db():
    """Diagnostic route to test database connection"""
    try:
        result = execute_query(
            "SELECT COUNT(*) as count FROM admin",
            fetch_one=True
        )
        return f"✓ Database connection successful! Admin users: {result['count']}"
    except Exception as e:
        return f"✗ Database Error: {str(e)}", 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            admin = execute_query(
                "SELECT * FROM admin WHERE username = %s", 
                (username,),
                fetch_one=True
            )
            
            if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
                session['admin_id'] = admin['id']
                session['admin_username'] = admin['username']
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid credentials', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            print(f"Admin login error: {e}")
    
    return render_template('admin/login.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        
        try:
            cursor = get_db_cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
            student = cursor.fetchone()
            cursor.close()
            
            if student and bcrypt.checkpw(password.encode('utf-8'), student['password'].encode('utf-8')):
                session['student_id'] = student['id']
                session['student_student_id'] = student['student_id']
                session['student_name'] = student['name']
                flash('Login successful!', 'success')
                return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid credentials', 'danger')
        except Exception as e:
            flash(f'Database Error: {str(e)}', 'danger')
            print(f"Student login error: {e}")
    
    return render_template('student/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/student/logout')
def student_logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    cursor = get_db_cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as total_students FROM students")
    total_students = cursor.fetchone()['total_students']
    
    # Get today's meal counts
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN breakfast = 1 THEN 1 ELSE 0 END) as breakfast_count,
            SUM(CASE WHEN lunch = 1 THEN 1 ELSE 0 END) as lunch_count,
            SUM(CASE WHEN dinner = 1 THEN 1 ELSE 0 END) as dinner_count
        FROM meal_confirmation 
        WHERE date = %s
    """, (today,))
    meal_counts = cursor.fetchone()
    
    # Get current month expenses
    current_month = date.today().strftime('%Y-%m')
    cursor.execute("""
        SELECT SUM(amount) as total_expenses 
        FROM expenses 
        WHERE DATE_FORMAT(date, '%Y-%m') = %s
    """, (current_month,))
    monthly_expenses = cursor.fetchone()['total_expenses'] or 0
    
    # Get pending complaints
    cursor.execute("SELECT COUNT(*) as pending_complaints FROM complaints WHERE status = 'pending'")
    pending_complaints = cursor.fetchone()['pending_complaints']
    
    cursor.close()
    
    return render_template('admin/dashboard.html', 
                         total_students=total_students,
                         meal_counts=meal_counts,
                         monthly_expenses=monthly_expenses,
                         pending_complaints=pending_complaints)

# Student Management
@app.route('/admin/students')
@admin_required
def manage_students():
    students = execute_query(
        "SELECT * FROM students ORDER BY name",
        fetch_all=True
    )
    return render_template('admin/students.html', students=students)

@app.route('/admin/students/add', methods=['GET', 'POST'])
@admin_required
def add_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        hostel_room = request.form['hostel_room']
        branch = request.form['branch']
        password = request.form['password']
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            execute_query(
                """
                INSERT INTO students (student_id, name, hostel_room, branch, password)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (student_id, name, hostel_room, branch, hashed_password)
            )
            flash('Student added successfully!', 'success')
            return redirect(url_for('manage_students'))
        except Exception as e:
            flash(f'Error adding student: {str(e)}', 'danger')
            print(f"Add student error: {e}")
    
    return render_template('admin/add_student.html')

@app.route('/admin/students/edit/<int:student_id>', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    cursor = get_db_cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        hostel_room = request.form['hostel_room']
        branch = request.form['branch']
        password = request.form.get('password')
        
        if password:
            # Update with new password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                UPDATE students 
                SET name = %s, hostel_room = %s, branch = %s, password = %s
                WHERE id = %s
            """, (name, hostel_room, branch, hashed_password, student_id))
        else:
            # Update without changing password
            cursor.execute("""
                UPDATE students 
                SET name = %s, hostel_room = %s, branch = %s
                WHERE id = %s
            """, (name, hostel_room, branch, student_id))
        
        commit_db()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('manage_students'))
    
    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    
    return render_template('admin/edit_student.html', student=student)

@app.route('/admin/students/delete/<int:student_id>')
@admin_required
def delete_student(student_id):
    cursor = get_db_cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    commit_db()
    cursor.close()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('manage_students'))

# Menu Management
@app.route('/admin/menu')
@admin_required
def manage_menu():
    menu_items = execute_query(
        "SELECT * FROM menu ORDER BY date DESC LIMIT 7",
        fetch_all=True
    )
    return render_template('admin/menu.html', menu_items=menu_items)

@app.route('/admin/menu/add', methods=['GET', 'POST'])
@admin_required
def add_menu():
    if request.method == 'POST':
        menu_date = request.form['date']
        breakfast = request.form['breakfast']
        lunch = request.form['lunch']
        dinner = request.form['dinner']
        
        try:
            execute_query(
                """
                INSERT INTO menu (date, breakfast, lunch, dinner)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                breakfast = VALUES(breakfast),
                lunch = VALUES(lunch),
                dinner = VALUES(dinner)
                """,
                (menu_date, breakfast, lunch, dinner)
            )
            flash('Menu added/updated successfully!', 'success')
            return redirect(url_for('manage_menu'))
        except Exception as e:
            flash(f'Error adding menu: {str(e)}', 'danger')
            print(f"Add menu error: {e}")
    
    return render_template('admin/add_menu.html')

@app.route('/admin/menu/edit/<int:menu_id>', methods=['GET', 'POST'])
@admin_required
def edit_menu(menu_id):
    cursor = get_db_cursor()
    
    if request.method == 'POST':
        menu_date = request.form['date']
        breakfast = request.form['breakfast']
        lunch = request.form['lunch']
        dinner = request.form['dinner']
        
        cursor.execute("""
            UPDATE menu 
            SET date = %s, breakfast = %s, lunch = %s, dinner = %s
            WHERE id = %s
        """, (menu_date, breakfast, lunch, dinner, menu_id))
        commit_db()
        flash('Menu updated successfully!', 'success')
        return redirect(url_for('manage_menu'))
    
    cursor.execute("SELECT * FROM menu WHERE id = %s", (menu_id,))
    menu = cursor.fetchone()
    cursor.close()
    
    return render_template('admin/edit_menu.html', menu=menu)

@app.route('/admin/menu/delete/<int:menu_id>')
@admin_required
def delete_menu(menu_id):
    cursor = get_db_cursor()
    cursor.execute("DELETE FROM menu WHERE id = %s", (menu_id,))
    commit_db()
    cursor.close()
    flash('Menu deleted successfully!', 'success')
    return redirect(url_for('manage_menu'))

# Expense Management
@app.route('/admin/expenses')
@admin_required
def manage_expenses():
    expenses = execute_query(
        "SELECT * FROM expenses ORDER BY date DESC",
        fetch_all=True
    )
    total_amount = sum(expense['amount'] for expense in expenses) if expenses else 0
    return render_template('admin/expenses.html', expenses=expenses, total_amount=total_amount)

@app.route('/admin/expenses/add', methods=['GET', 'POST'])
@admin_required
def add_expense():
    if request.method == 'POST':
        expense_date = request.form['date']
        category = request.form['category']
        description = request.form['description']
        amount = request.form['amount']
        
        cursor = get_db_cursor()
        cursor.execute("""
            INSERT INTO expenses (date, category, description, amount)
            VALUES (%s, %s, %s, %s)
        """, (expense_date, category, description, amount))
        commit_db()
        cursor.close()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('manage_expenses'))
    
    return render_template('admin/add_expense.html')

@app.route('/admin/expenses/delete/<int:expense_id>')
@admin_required
def delete_expense(expense_id):
    cursor = get_db_cursor()
    cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
    commit_db()
    cursor.close()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('manage_expenses'))

# Complaint Management
@app.route('/admin/complaints')
@admin_required
def manage_complaints():
    complaints = execute_query(
        """
        SELECT c.*, s.name as student_name, s.student_id 
        FROM complaints c 
        JOIN students s ON c.student_id = s.id 
        ORDER BY c.created_at DESC
        """,
        fetch_all=True
    )
    return render_template('admin/complaints.html', complaints=complaints)

@app.route('/admin/complaints/resolve/<int:complaint_id>')
@admin_required
def resolve_complaint(complaint_id):
    cursor = get_db_cursor()
    cursor.execute("""
        UPDATE complaints 
        SET status = 'resolved', resolved_at = NOW() 
        WHERE id = %s
    """, (complaint_id,))
    commit_db()
    cursor.close()
    flash('Complaint marked as resolved!', 'success')
    return redirect(url_for('manage_complaints'))

# Notice Management
@app.route('/admin/notices')
@admin_required
def manage_notices():
    notices = execute_query(
        "SELECT * FROM notices ORDER BY created_at DESC",
        fetch_all=True
    )
    return render_template('admin/notices.html', notices=notices)

@app.route('/admin/notices/add', methods=['GET', 'POST'])
@admin_required
def add_notice():
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        priority = request.form['priority']
        
        cursor = get_db_cursor()
        cursor.execute("""
            INSERT INTO notices (title, message, priority)
            VALUES (%s, %s, %s)
        """, (title, message, priority))
        commit_db()
        cursor.close()
        flash('Notice posted successfully!', 'success')
        return redirect(url_for('manage_notices'))
    
    return render_template('admin/add_notice.html')

@app.route('/admin/notices/delete/<int:notice_id>')
@admin_required
def delete_notice(notice_id):
    cursor = get_db_cursor()
    cursor.execute("DELETE FROM notices WHERE id = %s", (notice_id,))
    commit_db()
    cursor.close()
    flash('Notice deleted successfully!', 'success')
    return redirect(url_for('manage_notices'))

@app.route('/admin/food-ratings')
@admin_required
def manage_food_ratings():
    cursor = get_db_cursor()
    
    # Get all food ratings with student information
    cursor.execute("""
        SELECT fr.*, s.name, s.student_id as student_number
        FROM food_ratings fr
        JOIN students s ON fr.student_id = s.id
        ORDER BY fr.created_at DESC
    """)
    ratings = cursor.fetchall()
    
    # Calculate average ratings
    cursor.execute("""
        SELECT meal_type, AVG(rating) as avg_rating, COUNT(*) as total_ratings
        FROM food_ratings
        GROUP BY meal_type
    """)
    rating_stats = cursor.fetchall()
    
    cursor.close()
    
    return render_template('admin/food_ratings.html', 
                         ratings=ratings, 
                         rating_stats=rating_stats)

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session['student_id']
    today = date.today().strftime('%Y-%m-%d')
    
    today_menu = execute_query(
        "SELECT * FROM menu WHERE date = %s", (today,), fetch_one=True
    )
    meal_confirmation = execute_query(
        """
        SELECT * FROM meal_confirmation 
        WHERE student_id = %s AND date = %s
        """, (student_id, today), fetch_one=True
    )
    notices = execute_query(
        "SELECT * FROM notices ORDER BY created_at DESC LIMIT 3",
        fetch_all=True
    )
    complaints = execute_query(
        """
        SELECT * FROM complaints 
        WHERE student_id = %s 
        ORDER BY created_at DESC LIMIT 3
        """, (student_id,), fetch_all=True
    )
    
    return render_template('student/dashboard.html', 
                         today_menu=today_menu,
                         meal_confirmation=meal_confirmation,
                         notices=notices,
                         complaints=complaints)

# View Menu
@app.route('/student/menu')
@student_required
def view_menu():
    today = date.today()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    
    menu_items = execute_query(
        """
        SELECT * FROM menu 
        WHERE date BETWEEN %s AND %s 
        ORDER BY date
        """, (start_date, end_date), fetch_all=True
    )
    
    return render_template('student/menu.html', menu_items=menu_items)

# Meal Confirmation
@app.route('/student/meal-confirmation', methods=['GET', 'POST'])
@student_required
def meal_confirmation():
    cursor = get_db_cursor()
    student_id = session['student_id']
    
    if request.method == 'POST':
        confirmation_date = request.form['date']
        breakfast = 1 if request.form.get('breakfast') else 0
        lunch = 1 if request.form.get('lunch') else 0
        dinner = 1 if request.form.get('dinner') else 0
        
        cursor.execute("""
            INSERT INTO meal_confirmation 
            (student_id, date, breakfast, lunch, dinner)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            breakfast = VALUES(breakfast),
            lunch = VALUES(lunch),
            dinner = VALUES(dinner)
        """, (student_id, confirmation_date, breakfast, lunch, dinner))
        commit_db()
        flash('Meal confirmation updated successfully!', 'success')
    
    # Get today's confirmation
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT * FROM meal_confirmation 
        WHERE student_id = %s AND date = %s
    """, (student_id, today))
    confirmation = cursor.fetchone()
    
    cursor.close()
    
    return render_template('student/meal_confirmation.html', 
                         confirmation=confirmation,
                         today=today)

# Student Complaints
@app.route('/student/complaints', methods=['GET', 'POST'])
@student_required
def student_complaints():
    cursor = get_db_cursor()
    student_id = session['student_id']
    
    if request.method == 'POST':
        subject = request.form['subject']
        message = request.form['message']
        
        cursor.execute("""
            INSERT INTO complaints (student_id, subject, message)
            VALUES (%s, %s, %s)
        """, (student_id, subject, message))
        commit_db()
        flash('Complaint submitted successfully!', 'success')
    
    # Get student's complaints
    cursor.execute("""
        SELECT * FROM complaints 
        WHERE student_id = %s 
        ORDER BY created_at DESC
    """, (student_id,))
    complaints = cursor.fetchall()
    cursor.close()
    
    return render_template('student/complaints.html', complaints=complaints)

# Food Rating
@app.route('/student/food-rating', methods=['GET', 'POST'])
@student_required
def food_rating():
    cursor = get_db_cursor()
    student_id = session['student_id']
    
    if request.method == 'POST':
        rating_date = request.form['date']
        meal_type = request.form['meal_type']
        rating = request.form['rating']
        feedback = request.form.get('feedback', '')
        
        cursor.execute("""
            INSERT INTO food_ratings 
            (student_id, date, meal_type, rating, feedback)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            rating = VALUES(rating),
            feedback = VALUES(feedback)
        """, (student_id, rating_date, meal_type, rating, feedback))
        commit_db()
        flash('Food rating submitted successfully!', 'success')
    
    # Get today's menu for rating
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM menu WHERE date = %s", (today,))
    today_menu = cursor.fetchone()
    
    cursor.close()
    
    return render_template('student/food_rating.html', 
                         today_menu=today_menu,
                         today=today)

if __name__ == '__main__':
    app.run(debug=True)
