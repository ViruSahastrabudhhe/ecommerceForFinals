from flask import *
from flask_mail import *
from werkzeug.security import *
import mysql.connector
from mysql.connector import Error
from models import *

routes_bp = Blueprint("routes", __name__, static_folder='static', template_folder='templates')

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
@routes_bp.route("/")
def welcome():
    return redirect(url_for('routes.login'))

@routes_bp.route('/home')
def home():
    return render_template('home.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@routes_bp.route('/test')
def test():
    return render_template('test.html')

# users ----------------------------------------------------------------------------------------------
@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'admin'
        ifArchived = False

        if isLoginFormInvalid(email, password):
            flash("Please input in the fields!", category='error')
            return redirect(url_for('routes.login'))
        
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('routes.login'))
        
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
                return redirect(url_for('routes.home'))
            else:
                flash('Incorrect credentials. Try again!', category='error')
        else:
            flash('Incorrect credentials. Try again!', category='error')

    return render_template('login.html')

@routes_bp.route("/signUp", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['fName'] + ' ' + request.form['lName']
        email = request.form['emailSignUp']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        # security measure, prevents user from leaving fields blank
        if isSignUpFormInvalid(email, password, confirmPassword, username):
            flash("Please input in the fields!", category='error')
            return redirect(url_for('routes.signUp'))
        # security measure, prevents user from inputting invalid email (no @)
        elif not isEmailValid(email): 
            flash('Email invalid!', category='error')
            return redirect(url_for('routes.signUp'))
        # security measure, prevents user from making a password with <8 characters
        elif not isPasswordValid(password):
            flash('Password must not be <8 characters!', category='error')
            return redirect(url_for('routes.signUp'))
        # password must be equal to confirm pass
        elif password!=confirmPassword:
            flash('Password does not match!', category='error')
            return redirect(url_for('routes.signUp'))
        
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('routes.signUp'))

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
            return redirect(url_for('routes.signUp'))
        finally:
            cursor.close()
            conn.close()
                
        return redirect(url_for('routes.login'))
        
    return render_template('sign_up.html', purpose="signUp")

@routes_bp.route("/forgotPassword", methods=['GET', 'POST'])
def forgotPassword():
    if request.method=='POST':
        email=request.form['emailForgotPassword']

        if not isEmailValid(email):
            flash("Email invalid!", category='error')
            return render_template('sign_up.html', purpose="forgotPassword")

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION LOL', category='error')
            return redirect(url_for('routes.login'))
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM accounts WHERE accountEmail='{email}'")
        record = cursor.fetchone()

        if record:
            flash("Password reset request sent!", category='success')
            return redirect(url_for('routes.login'))
        else:
            flash("Email does not existo!", category='error')
            return render_template('sign_up.html', purpose="forgotPassword")

    return render_template('sign_up.html', purpose="forgotPassword")

@routes_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.login'))

# seller ----------------------------------------------------------------------------------------------
@routes_bp.route('/renderBuyerBecomeSeller')
def renderBuyerBecomeSeller():
    return render_template('home.html', purpose="renderBuyerBecomeSeller", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@routes_bp.route('/requestToBecomeSeller', methods=['GET', 'POST'])
def requestToBecomeSeller():
    if request.method=="POST":
        id = session['accountID']
        email = session['accountEmail']
        requestType = "BUYER TO BE SELLER"

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='danger')
            return redirect(url_for('routes.login'))   
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO requests (accountID, accountEmail, requestType, requestArchived) VALUES (%s, %s, %s, %s)', (id, email, requestType, 0))
            conn.commit()
            flash("CREATED NEW REQUEST", category="success")
        except mysql.connector.IntegrityError:  
            flash("REQUEST ALREADY EXISTO", category='error')
            return render_template('home.html', purpose='renderBuyerBecomeSeller', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('routes.home'))
    
    return render_template('home.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@routes_bp.route("/renderSellProduct", methods=['GET', 'POST'])
def renderSellProduct():
    return render_template('home.html', purpose="renderSellProduct", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@routes_bp.route("/requestToSellProduct", methods=['GET', 'POST'])
def requestToSellProduct():
    if request.method=="POST":
        id = session['accountID']
        email = session['accountEmail']
        requestType = "SELL A PRODUCT"

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='danger')
            return redirect(url_for('routes.home'))   
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO requests (accountID, accountEmail, requestType, requestArchived) VALUES (%s, %s, %s, %s)', (id, email, requestType, 0))
            conn.commit()
            flash("CREATED NEW REQUEST", category="success")
        except mysql.connector.IntegrityError:  
            flash("REQUEST ALREADY EXISTO", category='error')
            return render_template('home.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('routes.home'))
    
    return render_template('home.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

# admin ----------------------------------------------------------------------------------------------
@routes_bp.route('/homeAdmin')
def homeAdmin():
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='danger')
        return redirect(url_for('routes.login'))   
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requests WHERE requestArchived=0")
        rows=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('home_admin.html', email=session['accountEmail'], dbhtml=rows)
    except Error as e:
        flash(f'{e}', category='error')
        logout()

@routes_bp.route('/loginAdmin', methods=['GET', 'POST'])
def loginAdmin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'admin'

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='danger')
            return redirect(url_for('routes.loginAdmin'))
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE accountEmail=%s AND accountPassword=%s AND accountRole=%s', (email, password, role))
        record = cursor.fetchone()

        # SESSION COOKIES
        if record:
            session['loggedIn'] = True
            session['accountID'] = record['accountID']
            session['accountEmail'] = record['accountEmail']
            session['accountRole'] = record['accountRole']
            return redirect(url_for('routes.homeAdmin'))
        else:
            flash('Incorrect credentials. Try again!', category='danger')

    return render_template('login_admin.html')

@routes_bp.route('/adminRequestInteraction/<email>', methods=['GET', 'POST'])
def adminRequestInteraction(email):
    if request.method=='POST':
        approval = request.form['interact']

        if approval=="accept":
            updateBuyerToSeller(email)
            flash('Approved request of buyer to become seller!',category="success")
            return redirect(url_for('routes.homeAdmin'))
        elif approval=="decline":
            rejectBuyerToSeller(email)
            flash('Declined request of buyer to become seller!',category="error")
            return redirect(url_for('routes.homeAdmin'))
        
    return render_template('home_admin.html', accountEmail=email)

# functions ----------------------------------------------------------------------------------------------
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
        return redirect(url_for('routes.signUp'))

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
        return redirect(url_for('routes.signUp'))
    finally:
        cursor.close()
        conn.close()

def updateBuyerToSeller(email: str):
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('routes.homeAdmin'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f'UPDATE accounts SET accountRole="seller" WHERE accountEmail="{email}"')
    cursor.execute(f'UPDATE requests SET requestArchived=1 WHERE accountEmail="{email}"')
    '''
        FIXME: WONT UPDATE SHIT
        FIXED: NEED FOR DB TO COMMIT LOL FUCK ME SHIT WAS SO BASIC XDDD
    '''
    conn.commit()
    cursor.close()

def rejectBuyerToSeller(email: str):
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('routes.homeAdmin'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f'UPDATE requests SET requestArchived=1 WHERE accountEmail="{email}"')
    '''
        FIXME: WONT UPDATE SHIT
        FIXED: NEED FOR DB TO COMMIT LOL FUCK ME SHIT WAS SO BASIC XDDD
    '''
    conn.commit()
    cursor.close()