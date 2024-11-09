from awesomers import app, mail
from flask import render_template, redirect, session, flash, request, url_for
from flask_mail import Message
from email.mime.text import MIMEText
import os
import smtplib
from smtplib import SMTP
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection, generateToken, verifyToken
from werkzeug.security import *

# routes are like labels using goto switches
@app.route("/")
def welcome():
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if session['accountRole']=='seller':
        return render_template('dashboard/dashboard_seller.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
    elif session['accountRole']=='buyer':
        return render_template('dashboard/dashboard_buyer.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@app.route('/test')
def test():
    return render_template('accounts/forgot_password.html', legend="TEST")

# users ----------------------------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['emailLogin']
        password = request.form['password']
        role = 'admin'
        ifArchived = False

        if isLoginFormEmpty(email, password):
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
        if record is None:
            flash('Email does not exist! Try again.', category='error')
            return redirect(url_for('login'))

        if check_password_hash(record['accountPassword'], password):
            session['loggedIn'] = True
            session['accountID'] = record['accountID']
            session['accountEmail'] = record['accountEmail']
            session['accountUsername'] = record['accountUsername']
            session['accountRole'] = record['accountRole']
            return redirect(url_for('home'))
        else:
            flash('Incorrect password! Try again.', category='error')

    return render_template('accounts/login.html', legend="Login")

@app.route("/signUp", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['fName'] + ' ' + request.form['lName']
        email = request.form['emailSignUp']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        if isSignUpFormEmpty(email, password, confirmPassword, username):
            flash("Please input in the fields!", category='error')
            return redirect(url_for('signUp'))
        elif not isEmailFormatValid(email): 
            flash('Email invalid!', category='error')
            return redirect(url_for('signUp'))
        elif not isPasswordLongEnough(password):
            flash('Password must not be <8 characters!', category='error')
            return redirect(url_for('signUp'))
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
        
    return render_template('accounts/sign_up.html', legend="Sign up")

@app.route('/resetPassword/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    email = verifyToken(token, expiration=3600)
    # '''
    #     FIXME: WOULDNT REDIRECT HERE, CAUSING IT TO UPDATE ALL USER PASSWORDS TO WHATEVER
    #     FIXED: 'email==False' instead of 'email is None'
    # '''
    if email==False:
        flash('Invalid token or token has expired. Please try again!', category='error')
        return redirect(url_for('login'))
    
    if request.method=='POST':
        newPassword=request.form['newPassword']
        confirmNewPassword=request.form['confirmNewPassword']

        if newPassword!=confirmNewPassword:
            flash('Passwords do not match!', category='error')
            return redirect(url_for('resetPassword', token=token))

        if not isPasswordLongEnough(newPassword):
            flash('Password must not be <8 characters!', category='error')
            return redirect(url_for('resetPassword', token=token))

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION LOL', category='error')
            return redirect(url_for('requestPasswordReset'))
        
        hashedPassword = generate_password_hash(newPassword, method="pbkdf2:sha256")
        cursor=conn.cursor()

        try:
            cursor.execute('UPDATE accounts SET accountPassword=%s WHERE accountEmail=%s', (hashedPassword, email))
            conn.commit()
            flash('Password successfully reset!', category='success')
        except:
            flash('An unexpected error has occurred!', category='error')
            return redirect(url_for('login'))
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('login'))

    return render_template('accounts/reset_password.html', legend='Reset password', userToken=token, userEmail=email)
        
@app.route("/requestPasswordReset", methods=['GET', 'POST'])
def requestPasswordReset():
    if request.method=='POST':
        email=request.form['emailForgotPassword']
        role='admin'
        ifArchived=False

        if not isEmailFormatValid(email):
            flash("Email invalid!", category='error')
            return redirect(url_for('requestPasswordReset'))

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION LOL', category='error')
            return redirect(url_for('login'))
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM accounts WHERE accountEmail='{email}' AND accountRole!='{role}' AND accountArchived={ifArchived}")
        record = cursor.fetchone()

        if record is None:
            flash("Email does not existo!", category='error')
            return redirect(url_for('requestPasswordReset'))
        
        try:
            sendForgotPasswordMail(email)
            flash("Password reset request sent!", category='success')
        except:
            flash("Failed to send password request!", category='error')
            return redirect(url_for('requestPasswordReset'))
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('login'))
    
    return render_template('accounts/forgot_password.html',  legend="Forgot password")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# seller ----------------------------------------------------------------------------------------------
@app.route('/renderBuyerBecomeSeller')
def renderBuyerBecomeSeller():
    return render_template('dashboard/dashboard_buyer.html', purpose="renderBuyerBecomeSeller", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@app.route('/requestToBecomeSeller', methods=['GET', 'POST'])
def requestToBecomeSeller():
    if request.method=="POST":
        id = session['accountID']
        email = session['accountEmail']
        requestType = "BUYER TO BE SELLER"

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('login'))   
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO requests (accountID, accountEmail, requestType, requestArchived) VALUES (%s, %s, %s, %s)', (id, email, requestType, 0))
            conn.commit()
            flash("CREATED NEW REQUEST", category="success")
        except mysql.connector.IntegrityError:  
            flash("REQUEST ALREADY EXISTO", category='error')
            return redirect(url_for('renderBuyerBecomeSeller'))
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('home'))
    
    return render_template('dashboard/dashboard_buyer.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@app.route("/renderSellProduct", methods=['GET', 'POST'])
def renderSellProduct():
    return render_template('dashboard/dashboard_seller.html', purpose="renderSellProduct", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@app.route("/requestToSellProduct", methods=['GET', 'POST'])
def requestToSellProduct():
    if request.method=="POST":
        id = session['accountID']
        email = session['accountEmail']
        requestType = "SELL A PRODUCT"

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('home'))   
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO requests (accountID, accountEmail, requestType, requestArchived) VALUES (%s, %s, %s, %s)', (id, email, requestType, 0))
            conn.commit()
            flash("CREATED NEW REQUEST", category="success")
        except mysql.connector.IntegrityError:  
            flash("REQUEST ALREADY EXISTO", category='error')
            return redirect(url_for('renderSellProduct'))
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('home'))
    
    return render_template('dashboard/dashboard_seller.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

# admin ----------------------------------------------------------------------------------------------
@app.route('/homeAdmin')
def homeAdmin():
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('loginAdmin'))   
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requests WHERE requestArchived=0")
        rows=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('admin/home_admin.html', email=session['accountEmail'], dbhtml=rows)
    except Error as e:
        flash(f'{e}', category='error')
        logout()

@app.route('/loginAdmin', methods=['GET', 'POST'])
def loginAdmin():
    if request.method == 'POST':
        email = request.form['emailAdmin']
        password = request.form['password']
        role = 'admin'
        ifArchived = False

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('loginAdmin'))
        
        cursor = conn.cursor(dictionary=True)
        '''
            FIXME: WONT LOGIN TO ALREADY EXISTING ADMIN ACCOUNT
            FIXED: DONT QUERY PASSWORD, FORM PASSWORD != HASHED PASSWORD IN DB. LET CHECK_PASSWORD_HASH DO THAT TRICK
        '''
        cursor.execute('SELECT * FROM accounts WHERE accountEmail=%s AND accountRole=%s AND accountArchived=%s', (email, role, ifArchived))
        record = cursor.fetchone()

        # SESSION COOKIES
        if record:
            if check_password_hash(record['accountPassword'], password):
                session['loggedIn'] = True
                session['accountID'] = record['accountID']
                session['accountEmail'] = record['accountEmail']
                session['accountRole'] = record['accountRole']
                return redirect(url_for('homeAdmin'))
            else:
                flash('Incorrect password! Try again.', category='error')
        else:
            flash('Email does not exist! Try again.', category='error')

    return render_template('admin/login_admin.html', legend='Admin Login')

@app.route('/adminRequestInteraction/<email>', methods=['GET', 'POST'])
def adminRequestInteraction(email):
    if request.method=='POST':
        approval = request.form['interact']

        if approval=="accept":
            updateBuyerToSeller(email)
            flash('Approved request of buyer to become seller!',category="success")
            return redirect(url_for('homeAdmin'))
        elif approval=="decline":
            rejectBuyerToSeller(email)
            flash('Declined request of buyer to become seller!',category="error")
            return redirect(url_for('homeAdmin'))
        
    return render_template('admin/home_admin.html', accountEmail=email)

# functions ----------------------------------------------------------------------------------------------
def isSignUpFormEmpty(email: str, password: str, confirmPassword: str, username: str):
    if email==" " or password==" " or confirmPassword==" " or username==" ":
        return True

def isLoginFormEmpty(email: str, password: str):
    if email==" " or password==" ":
        return True

def isEmailFormatValid(email: str):
    if "@" in email and len(email)>10:
        return True
    
def isPasswordLongEnough(password: str):
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
        flash("Account already exists", category='error')
        return redirect(url_for('signUp'))
    finally:
        cursor.close()
        conn.close()

def updateBuyerToSeller(email: str):
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homeAdmin'))
    
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
        return redirect(url_for('homeAdmin'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f'UPDATE requests SET requestArchived=1 WHERE accountEmail="{email}"')
    '''
        FIXME: WONT UPDATE SHIT
        FIXED: NEED FOR DB TO COMMIT LOL FUCK ME SHIT WAS SO BASIC XDDD
    '''
    conn.commit()
    cursor.close()

def sendForgotPasswordMail(email):
    token=generateToken(email)
    msg=Message(
        subject='Password reset request sent!',
        recipients=['awesomersecommerce@gmail.com'],
        sender='example@demomailtrap.com'
    )
    msg.body=f''' To reset your password. Please follow the link below.
    
    {url_for('resetPassword', token=token, _external=True)}

    ...

    If you didn't send a password reset request, please ignore this message.

    '''
    mail.send(msg)
    return "Message sent!"