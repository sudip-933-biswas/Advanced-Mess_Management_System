import mysql.connector
import bcrypt

DB_CONFIG={'host':'localhost','port':3306,'user':'root','password':'gietu','database':'mess_management'}
try:
    conn=mysql.connector.connect(**DB_CONFIG)
    print('connected')
    cursor=conn.cursor()
    hashed=bcrypt.hashpw('pass'.encode(),bcrypt.gensalt()).decode()
    cursor.execute("INSERT IGNORE INTO students(student_id,name,hostel_room,branch,password) VALUES(%s,%s,%s,%s,%s)",["testid","Test Name","R1","CS",hashed])
    conn.commit()
    print('inserted')
    cursor.close()
    conn.close()
except Exception as e:
    print('error',e)
