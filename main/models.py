from main import app
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",  
            user="root",       
            password="",       
            database="ecommerce"
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    
def generateToken(email):
    serial=Serializer(app.config['SECRET_KEY'])
    return serial.dumps(email, salt=app.config['SECRET_KEY'])

def verifyToken(token, expiration=3600):
    serial=Serializer(app.config['SECRET_KEY'])
    try:
        email = serial.loads(
            token,
            salt=app.config['SECRET_KEY'],
            max_age=expiration
        )
    except:
        return False
    return email