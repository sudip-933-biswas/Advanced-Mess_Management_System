import mysql.connector
from mysql.connector import Error

def fix_menu_table():
    connection = None
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='gietu',
            database='mess_management'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Drop existing menu table if it exists (it's incomplete)
            cursor.execute("DROP TABLE IF EXISTS menu")
            print("✓ Dropped old menu table")
            
            # Recreate menu table with all required columns
            cursor.execute("""
                CREATE TABLE menu (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    breakfast TEXT,
                    lunch TEXT,
                    dinner TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_date (date)
                )
            """)
            print("✓ Created new menu table with all columns")
            
            connection.commit()
            print("\n✅ Menu table fixed successfully!")
            
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    fix_menu_table()
