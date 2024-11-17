from . import users
from flask import render_template, redirect, url_for, flash, session, request
from awesomers import mail
from flask_mail import Message
from email.mime.text import MIMEText
import os
import smtplib
from smtplib import SMTP
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection, generateToken, verifyToken
from werkzeug.security import *

@users.route('/')
def welcome():
    return redirect(url_for('users.login'))

@users.route('/test')
def test():
    return render_template('kaiAdmin/forms/forms.html')

# users ----------------------------------------------------------------------------------------------
@users.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['emailLogin']
        password = request.form['password']
        role = 'admin'
        ifArchived = False

        if isLoginFormEmpty(email, password):
            flash("Please input in the fields!", category='error')
            return redirect(url_for('users.login'))
        
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('users.login'))
        
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
            return redirect(url_for('users.login'))

        if check_password_hash(record['accountPassword'], password):
            session['loggedIn'] = True
            session['accountID'] = record['accountID']
            session['accountEmail'] = record['accountEmail']
            session['accountUsername'] = record['accountUsername']
            session['accountRole'] = record['accountRole']
            return redirect(url_for('homepage.home'))
        else:
            flash('Incorrect password! Try again.', category='error')

    return render_template('accounts/login.html', legend="Login")

@users.route("/signUp", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['fName'] + ' ' + request.form['lName']
        email = request.form['emailSignUp']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        if isSignUpFormEmpty(email, password, confirmPassword, username):
            flash("Please input in the fields!", category='error')
            return redirect(url_for('users.signUp'))
        elif not isEmailFormatValid(email): 
            flash('Email invalid!', category='error')
            return redirect(url_for('users.signUp'))
        elif not isPasswordLongEnough(password):
            flash('Password must be greater than 8 characters!', category='error')
            return redirect(url_for('users.signUp'))
        elif password!=confirmPassword:
            flash('Password does not match!', category='error')
            return redirect(url_for('users.signUp'))
        
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('users.signUp'))

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
            conn.rollback()
            flash("Account is already signed up!", category='error')
            return redirect(url_for('users.signUp'))
        finally:
            cursor.close()
            conn.close()
                
        return redirect(url_for('users.login'))
        
    return render_template('accounts/sign_up.html', legend="Sign up")

@users.route('/resetPassword/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    email = verifyToken(token, expiration=3600)
    # '''
    #     FIXME: WOULDNT REDIRECT HERE, CAUSING IT TO UPDATE ALL USER PASSWORDS TO WHATEVER
    #     FIXED: 'email==False' instead of 'email is None'
    # '''
    if email==False:
        flash('Invalid token or token has expired. Please try again!', category='error')
        return redirect(url_for('users.login'))
    
    if request.method=='POST':
        newPassword=request.form['newPassword']
        confirmNewPassword=request.form['confirmNewPassword']

        if newPassword!=confirmNewPassword:
            flash('Passwords do not match!', category='error')
            return redirect(url_for('users.resetPassword', token=token))

        if not isPasswordLongEnough(newPassword):
            flash('Password must not be <8 characters!', category='error')
            return redirect(url_for('users.resetPassword', token=token))

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION LOL', category='error')
            return redirect(url_for('users.requestPasswordReset'))
        
        hashedPassword = generate_password_hash(newPassword, method="pbkdf2:sha256")
        cursor=conn.cursor()

        try:
            cursor.execute('UPDATE accounts SET accountPassword=%s WHERE accountEmail=%s', (hashedPassword, email))
            conn.commit()
            flash('Password successfully reset!', category='success')
        except:
            conn.rollback()
            flash('An unexpected error has occurred!', category='error')
            return redirect(url_for('users.login'))
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('users.login'))

    return render_template('accounts/reset_password.html', legend='Reset password', userToken=token, userEmail=email)
        
@users.route("/requestPasswordReset", methods=['GET', 'POST'])
def requestPasswordReset():
    if request.method=='POST':
        email=request.form['emailForgotPassword']
        role='admin'
        ifArchived=False

        if not isEmailFormatValid(email):
            flash("Email invalid!", category='error')
            return redirect(url_for('users.requestPasswordReset'))

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION LOL', category='error')
            return redirect(url_for('users.login'))
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM accounts WHERE accountEmail='{email}' AND accountRole!='{role}' AND accountArchived={ifArchived}")
        record = cursor.fetchone()

        if record is None:
            flash("Email does not existo!", category='error')
            return redirect(url_for('users.requestPasswordReset'))
        else:
            try:
                sendForgotPasswordMail(email)
                flash("Password reset request sent!", category='success')
            except Error as e:
                conn.rollback()
                flash(f"{e}", category='error')
                return redirect(url_for('users.requestPasswordReset'))
            finally:
                cursor.close()
                conn.close()

        return redirect(url_for('users.login'))
    
    return render_template('accounts/forgot_password.html',  legend="Forgot password")

@users.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('users.login'))

# admin ----------------------------------------------------------------------------------------------
@users.route('/loginAdmin', methods=['GET', 'POST'])
def loginAdmin():
    if request.method == 'POST':
        email = request.form['emailAdmin']
        password = request.form['password']
        role = 'admin'
        ifArchived = False

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('users.loginAdmin'))
        
        cursor = conn.cursor(dictionary=True)
        '''
            FIXME: WONT LOGIN TO ALREADY EXISTING ADMIN ACCOUNT
            FIXED: DONT QUERY PASSWORD, FORM PASSWORD != HASHED PASSWORD IN DB. LET CHECK_PASSWORD_HASH DO THAT TRICK
        '''
        cursor.execute('SELECT * FROM accounts WHERE accountEmail=%s AND accountRole=%s AND accountArchived=%s', (email, role, ifArchived))
        record = cursor.fetchone()

        # SESSION COOKIES
        if record is None:
            flash('Email does not exist! Try again.', category='error')
            return redirect(url_for('users.loginAdmin'))
        
        if check_password_hash(record['accountPassword'], password):
            session['loggedIn'] = True
            session['accountID'] = record['accountID']
            session['accountEmail'] = record['accountEmail']
            session['accountRole'] = record['accountRole']
            return redirect(url_for('homepage.homeAdmin'))
        else:
            flash('Incorrect password! Try again.', category='error')

    return render_template('admin/login_admin.html', legend='Admin Login')

# methods ----------------------------------------------------------------------------------------------
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
        conn.rollback()
        flash("Account already exists", category='error')
        return redirect(url_for('signUp'))
    finally:
        cursor.close()
        conn.close()

def sendForgotPasswordMail(email: str):
    token=generateToken(email)
    msg=Message(
        subject='Password reset request!',
        sender='noreply@gmail.com',
        recipients=[f"{email}"]
    )
    msg.body = f''' To reset your password. Please follow the link below.

    {url_for('users.resetPassword', token=token, _external=True)}

    ...

    If you didn't send a password reset request, please ignore this message.

    '''
    mail.send(msg)
    return 'Password reset request sent!'