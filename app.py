from flask import *
import mysql.connector 
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'secret'

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
    
# routes are like labels using goto switches
@app.route("/")
def welcome():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html', email=session['accountEmail'], username=session['accountUsername'])

@app.route('/homeAdmin')
def homeAdmin():
    return render_template('home-admin.html', email=session['accountEmail'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'admin'
        ifArchived = False

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", 'danger')
            return redirect(url_for('login'))
        
        cursor = conn.cursor(dictionary=True)
        '''
        FIXME: for some reason, this is the wrong syntax? like wtf do u mean
        FIXED: use AND instead of , when filtering through multiple columns lol
        '''
        cursor.execute('SELECT * FROM accounts WHERE accountEmail=%s AND accountPassword=%s AND accountRole!=%s AND accountArchived=%s', (email, password, role, ifArchived))
        record = cursor.fetchone()

        # SESSION COOKIES
        if record:
            session['loggedIn'] = True
            session['accountID'] = record['accountID']
            session['accountEmail'] = record['accountEmail']
            session['accountRole'] = record['accountRole']
            session['accountUsername'] = record['accountUsername']
            return redirect(url_for('home'))
        else:
            flash('Incorrect credentials. Try again!', 'danger')

    return render_template('login.html')

@app.route('/loginAdmin', methods=['GET', 'POST'])
def loginAdmin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'admin'

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", 'danger')
            return redirect(url_for('loginAdmin'))
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE accountEmail=%s AND accountPassword=%s AND accountRole=%s', (email, password, role))
        record = cursor.fetchone()

        # SESSION COOKIES
        if record:
            session['loggedIn'] = True
            session['accountID'] = record['accountID']
            session['accountEmail'] = record['accountEmail']
            session['accountRole'] = record['accountRole']
            return render_template("home-admin.html")
        else:
            flash('Incorrect credentials. Try again!', 'danger')

    return render_template('login-admin.html')

@app.route("/signUp", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['fName'] + request.form['lName']
        role = 'buyer'
        ifArchived = False

        # security measure, prevents user from inputting invalid email
        if not isEmailValid(email): 
            return redirect(url_for('signUp'))

        # security measure, prevents user from making a password <8 characters
        if not isPasswordValid(password):
            return redirect(url_for('signUp'))

        # prevents no input from signing up
        if email == "" or password == "":
            flash("Please input in the fields")
            return redirect(url_for('signUp'))
        
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", 'danger')
            return redirect(url_for('signUp'))
        
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO accounts (accountEmail, accountPassword, accountUsername, accountRole, accountArchived) VALUES (%s, %s, %s, %s)', (email, password, username, role, ifArchived))
            conn.commit()
            flash("CREATED NEW ACCOUNT")
        except mysql.connector.IntegrityError:  
            flash("Email already exists!", 'danger')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('login'))

    return render_template('sign_up.html')

# @app.route('/buyerToSellerRequest')
# def buyerToSellerRequest():
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def isEmailValid(email: str):
    if "@" in email:
        return True
    
def isPasswordValid(password: str):
    if len(password) > 8:
        return True

if __name__ == '__main__':
    app.run(debug=True)