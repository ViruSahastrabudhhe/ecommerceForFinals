from flask import *
import mysql.connector 
from mysql.connector import Error
from werkzeug.security import *

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
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('home.html', email=session['accountEmail'], username=session['accountUsername'])

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'admin'
        ifArchived = False

        if isLoginFormInvalid(email, password):
            flash("Please input in the fields!", category='error')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('login'))
        
        cursor = conn.cursor(dictionary=True)
        '''
        FIXME: for some reason, this is the wrong syntax? like wtf do u mean
        FIXED: use AND instead of , when filtering through multiple columns lol
        '''
        cursor.execute('SELECT * FROM accounts WHERE accountEmail=%s AND accountRole!=%s AND accountArchived=%s', (email, role, ifArchived))
        record = cursor.fetchone()


        # SESSION COOKIES
        if record:
            if check_password_hash(record['accountPassword'], password):
                session['loggedIn'] = True
                session['accountID'] = record['accountID']
                session['accountEmail'] = record['accountEmail']
                session['accountUsername'] = record['accountUsername']
                session['accountRole'] = record['accountRole']
                return redirect(url_for('home'))
            else:
                flash('Incorrect credentials. Try again!', category='error')
        else:
            flash('Incorrect credentials. Try again!', category='error')

    return render_template('login.html')

@app.route("/signUp", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['fName'] + ' ' + request.form['lName']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        if isSignUpFormInvalid(email, password, confirmPassword, username):
            flash("Please input in the fields!", category='error')
            return redirect(url_for('signUp'))
        # security measure, prevents user from inputting invalid email (no @)
        elif not isEmailValid(email): 
            flash('Email invalid!', category='error')
            return redirect(url_for('signUp'))
        # security measure, prevents user from making a password with <8 characters
        elif not isPasswordValid(password):
            flash('Password must not be <8 characters!', category='error')
            return redirect(url_for('signUp'))
        # prevents no input from signing up
        elif password!=confirmPassword:
            flash('Password does not match!', category='error')
            return redirect(url_for('signUp'))
        
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('signUp'))

        '''
        FIXME: creates account even if email already exists and conditions are put in check!
        FIXED: establish sql index accountEmail as unique
        '''
        cursor = conn.cursor()
        hashedPassword = generate_password_hash(password, method="pbkdf2:sha256")
        
        try:
            cursor.execute('INSERT INTO accounts (accountEmail, accountPassword, accountUsername) VALUES (%s, %s, %s)', (email, hashedPassword, username))
            conn.commit()
            flash("Successfully signed up!", category='success')
        except mysql.connector.IntegrityError:
            flash("Account is already signed up!", category='error')
            return redirect(url_for('signUp'))
        finally:
            cursor.close()
            conn.close()
                
        return redirect(url_for('login'))
        
    return render_template('sign_up.html')

@app.route('/buyerBecomeSeller')
def buyerBecomeSeller():
    return render_template('buyerBecomeSeller.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'])

@app.route('/requestToBecomeSeller', methods=['GET', 'POST'])
def requestToBecomeSeller():
    if request.method=="POST":
        id = session['accountID']
        email = session['accountEmail']
        requestType = "BUYER TO BE SELLER"

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='danger')
            return redirect(url_for('login'))   
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO requests (accountID, accountEmail, requestType) VALUES (%s, %s, %s)', (id, email, requestType))
            conn.commit()
            flash("CREATED NEW REQUEST", category="success")
        except mysql.connector.IntegrityError:  
            flash("REQUEST ALREADY EXISTO", category='error')
            return redirect(url_for('buyerBecomeSeller'))
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('home'))
    
    return render_template('buyerBecomeSeller.html',id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# admin 
@app.route('/homeAdmin')
def homeAdmin():
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='danger')
        return redirect(url_for('login'))   
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests")
    rows=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('home_admin.html', email=session['accountEmail'], dbhtml=rows)

@app.route('/loginAdmin', methods=['GET', 'POST'])
def loginAdmin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'admin'

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='danger')
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
            return redirect(url_for('homeAdmin'))
        else:
            flash('Incorrect credentials. Try again!', category='danger')

    return render_template('login_admin.html')

@app.route('/adminRequestInteraction', methods=['GET', 'POST'])
def adminRequestInteraction():
    if request.method=='POST':
        approval = request.form['interact']

        if approval=="accept":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE accountRole FROM accounts')
            return "accepted"
        elif approval=="decline":
            return "declined"
        
    return "hello"

# functions
def isSignUpFormInvalid(email: str, password: str, confirmPassword: str, username: str):
    if email==" " or password==" " or confirmPassword==" " or username==" ":
        return True

def isLoginFormInvalid(email: str, password: str):
    if email==" " or password==" ":
        return True

def isEmailValid(email: str):
    if "@" in email and len(email)>10:
        return True
    
def isPasswordValid(password: str):
    if len(password) > 8:
        return True

def signUpAccount(email: str, username: str, password: str, confirmPassword: str):
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('signUp'))

    '''
    FIXME: creates account even if email already exists and conditions are put in check!
    FIXED: establish sql index accountEmail as unique
    '''
    cursor = conn.cursor()
    hashedPassword = generate_password_hash(password, method="pbkdf2:sha256")
    
    try:
        cursor.execute('INSERT INTO accounts (accountEmail, accountPassword, accountUsername) VALUES (%s, %s, %s)', (email, hashedPassword, username))
        conn.commit()
        flash("CREATED NEW ACCOUNT", category='success')
    except mysql.connector.IntegrityError:
        flash("Account already exists", category='danger')
        return redirect(url_for('signUp'))
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)