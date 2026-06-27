import mysql.connector
from mysql.connector import Error
import bcrypt

def create_database_and_tables():
    connection = None
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='2006'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS mess_management")
            cursor.execute("USE mess_management")
            
            # Create admin table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create students table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    hostel_room VARCHAR(50),
                    branch VARCHAR(100),
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create menu table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    breakfast TEXT,
                    lunch TEXT,
                    dinner TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_date (date)
                )
            """)
            
            # Create meal_confirmation table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meal_confirmation (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT,
                    date DATE NOT NULL,
                    breakfast BOOLEAN DEFAULT 0,
                    lunch BOOLEAN DEFAULT 0,
                    dinner BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    UNIQUE KEY unique_student_date (student_id, date)
                )
            """)
            
            # Create complaints table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS complaints (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT,
                    subject VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    status ENUM('pending', 'resolved') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP NULL,
                    FOREIGN KEY (student_id) REFERENCES students(id)
                )
            """)
            
            # Create expenses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    description TEXT,
                    amount DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create notices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NULL
                )
            """)
            
            # Create food_ratings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS food_ratings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT,
                    date DATE NOT NULL,
                    meal_type ENUM('breakfast', 'lunch', 'dinner') NOT NULL,
                    rating INT CHECK (rating >= 1 AND rating <= 5),
                    feedback TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    UNIQUE KEY unique_student_date_meal (student_id, date, meal_type)
                )
            """)
            
            # Insert default admin user (password: admin123)
            default_admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                INSERT IGNORE INTO admin (username, password) 
                VALUES ('admin', %s)
            """, (default_admin_password,))
            
            connection.commit()
            print("Database and tables created successfully!")
            print("Default admin credentials:")
            print("Username: admin")
            print("Password: admin123")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database_and_tables()
