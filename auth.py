from flask import *
import mysql.connector 
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

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
            flash("NO DB CONNECTION", category='danger')
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
            flash('Incorrect credentials. Try again!', category='danger')

    return render_template('login.html')

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
            return render_template("home-admin.html")
        else:
            flash('Incorrect credentials. Try again!', category='danger')

    return render_template('login-admin.html')

@app.route("/signUp", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['fName'] + ' ' + request.form['lName']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        if password!=confirmPassword:
            flash('Password does not match!', category='error')
            return redirect(url_for('signUp'))
        # security measure, prevents user from inputting invalid email (no @)
        elif not isEmailValid(email): 
            return redirect(url_for('signUp'))
        # security measure, prevents user from making a password with <8 characters
        elif not isPasswordValid(password):
            return redirect(url_for('signUp'))
        # prevents no input from signing up
        elif isSignUpFormInvalid(email, password, confirmPassword, username):
            flash("Please input in the fields!", category='error')
            return redirect(url_for('signUp'))
        else:
            signUpAccount(email, username, password, confirmPassword)
        
    return render_template('sign_up.html')

@app.route('/buyerBecomeSeller')
def buyerBecomeSeller():
    return render_template('buyerBecomeSeller.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'])

@app.route('/requestToBecomeSeller', methods=['GET', 'POST'])
def requestToBecomeSeller():
    if request.method=="POST":
        id = session['accountID']
        email = session['accountEmail']
        username = session['accountUsername']

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='danger')
            return redirect(url_for('login'))
        
        cursor = conn.cursor()
        # if a row doesnt have the ff account id -> insert into table
        cursor.execute(f'SELECT * FROM requests WHERE accountID = {id}')
        record = cursor.fetchone()
        
        if record:
            flash("DUPE", category='danger')
            return redirect(url_for('buyerBecomeSeller'))
        else:
            try:
                cursor.execute('INSERT INTO requests (accountID, accountEmail, accountUsername) VALUES (%s, %s, %s)', (id, email, username))
                conn.commit()
                flash("CREATED NEW REQUEST", category="success")
            except mysql.connector.IntegrityError:  
                flash("REQUEST ALREADY EXISTO", category='danger')
            # finally:
            #     cursor.close()
            #     conn.close()

        return redirect(url_for('home'))
    
    return render_template('buyerBecomeSeller.html',id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def isSignUpFormInvalid(email: str, password: str, confirmPassword: str, username: str):
    if email==" " or password==" " or confirmPassword==" " or username==" ":
        return True

def isEmailValid(email: str):
    if "@" in email:
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
    '''
    cursor = conn.cursor()
    hashedPassword = generate_password_hash(password, method="pbkdf2:sha256")
    # cursor.execute("SELECT * FROM accounts WHERE accountEmail ='%s'", email)
    # row = cursor.fetchone()
    
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

    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)