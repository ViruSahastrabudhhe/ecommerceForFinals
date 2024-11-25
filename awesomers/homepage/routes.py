from . import homepage
from flask import render_template, redirect, url_for, flash, session, request
from awesomers.users.routes import logout
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid as uuid
import pathlib
import os

@homepage.route('/home')
def home():
    if session['accountRole']=='seller':
        return render_template('homepage/seller/homepage_seller.html', id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    elif session['accountRole']=='buyer':
        return render_template('homepage/buyer/homepage_buyer.html', id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

# profile ----------------------------------------------------------------------------------------------
@homepage.route('/profile')
def profile():
    if session['accountRole'] == 'buyer':
        return redirect(url_for('profiles.buyerProfile'))
    if session['accountRole'] == 'seller':
        return redirect(url_for('profiles.sellerProfile'))

# buyer seller registration ----------------------------------------------------------------------------------------------
@homepage.route('/sellerRegistration')
def sellerRegistration():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    sql = "SELECT * FROM requests WHERE accountID=%s and accountEmail=%s"
    val = session['accountID'], session['accountEmail']
    cursor.execute(sql, val)
    requestRow = cursor.fetchone()

    if requestRow:
        validIDPictureFile = requestRow[6].decode(encoding="utf-8")
        bankDocumentPictureFile = requestRow[10].decode(encoding="utf-8")
        return render_template('homepage/buyer/seller_registration.html', legend="Seller registration", isRequest='true', requestInfo=requestRow, validIDPicture=validIDPictureFile, bankDocumentPicture=bankDocumentPictureFile, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

    try:
        cursor.execute(f"SELECT * FROM accounts WHERE accountID={session['accountID']}")
        row=cursor.fetchone()
        return render_template('homepage/buyer/seller_registration.html', legend="Seller registration", isRequest='false', accountInfo=row, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        flash(f"{e}", category='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()

@homepage.route('/sendSellerRegistrationRequest', methods=['GET', 'POST'])
def sendSellerRegistrationRequest():
    dateNow = datetime.now()
    
    if request.method=="POST":
        accountID = session['accountID']
        email = request.form['emailAddSR']
        fname = request.form['fNameAddSR']
        lname = request.form['lNameAddSR']
        validIDType = request.form['validIDTypeAddSR']
        validIDPicture = request.files['validIDPictureAddSR']
        validIDFullName = request.form['validIDFullNameAddSR']
        validIDNum = request.form['validIDNumAddSR']
        bankName = request.form['bankNameAddSR']
        bankDocumentPicture = request.files['bankDocumentPictureAddSR']
        bankAccName = request.form['bankAccNameAddSR']
        bankAccNum = request.form['bankAccNumAddSR']
        requestType = "Seller registration"
        requestDateCreated = dateNow
        requestArchived = 0

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))   
        
        cursor = conn.cursor()

        picFilename = secure_filename(validIDPicture.filename)
        picName = str(session['accountID']) + "_" + picFilename
        validIDPicture.save(os.path.join("awesomers/static/imgs", picName))
        validIDPicture = picName

        picFilename = secure_filename(bankDocumentPicture.filename)
        picName = str(session['accountID']) + "_" + picFilename
        bankDocumentPicture.save(os.path.join("awesomers/static/imgs", picName))
        bankDocumentPicture = picName
        
        try:
            sql = "INSERT INTO requests (accountID, accountEmail, accountFirstName, accountLastName, validIDType, pictureValidID, validIDFullName, validIDNum, bankName, pictureBankDocument, bankAccName, bankAccNum, requestType, requestDateCreated, requestArchived) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val = accountID, email, fname, lname, validIDType, validIDPicture, validIDFullName, validIDNum, bankName, bankDocumentPicture, bankAccName, bankAccNum, requestType, requestDateCreated, requestArchived
            cursor.execute(sql, val)
            conn.commit()
            flash("CREATED NEW REQUEST", category="success")
        except mysql.connector.IntegrityError:  
            conn.rollback()
            flash("REQUEST ALREADY EXISTO", category='error')
            return redirect(url_for('homepage.sellerRegistration'))
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('homepage.sellerRegistration'))
    
    return render_template('homepage/buyer/homepage_buyer.html', id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@homepage.route('/deleteSellerRegistrationRequest', methods=['GET', 'POST'])
def deleteSellerRegistrationRequest():
    if request.method=='POST':
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))
        
        cursor=conn.cursor()

        try:
            sql="DELETE FROM requests WHERE accountID=%s and accountEmail=%s"
            val=session['accountID'], session['accountEmail']
            cursor.execute(sql, val)
            conn.commit()
            flash('Deleted seller registration request!', category='success')
            return redirect(url_for('homepage.sellerRegistration'))
        except Error as e:
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('homepage.sellerRegistration'))
        finally:
            cursor.close()
            conn.close()

# address book ----------------------------------------------------------------------------------------------
@homepage.route('/addressBook')
def addressBook():
    if session['accountRole'] == 'buyer':
        if isProfileAndSellerEstablished()=="both":
            return render_template('homepage/buyer/address_book_buyer.html', legend="Address book", isAddress='true', isProfile='true', id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
        elif isProfileAndSellerEstablished()=="one":
            return render_template('homepage/buyer/address_book_buyer.html', legend="Address book", isAddress='false', isProfile='true', id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
        else:
            return render_template('homepage/buyer/address_book_buyer.html', legend="Address book", isAddress='false', isProfile='false', id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    else:
        return render_template('homepage/buyer/address_book_buyer.html', legend="Address book", isAddress='false', isProfile='false', id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

# seller ----------------------------------------------------------------------------------------------
@homepage.route("/redirectToSellerCenter")
def redirectToSellerCenter():
    return redirect(url_for('seller.sellerCenter'))

@homepage.route("/redirectToSellerBase")
def redirectToSellerBase():
    return redirect(url_for('seller.sellerBase'))

# admin ----------------------------------------------------------------------------------------------
@homepage.route('/homeAdmin')
def homeAdmin():
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('users.loginAdmin'))   

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM requests WHERE requestArchived=0")
        rows=cursor.fetchall()
        return render_template('admin/home_admin.html', email=session['accountEmail'], dbhtml=rows)
    except Error as e:
        flash(f'{e}', category='error')
        logout()
    finally:
        cursor.close()
        conn.close()

@homepage.route('/adminRequestInteraction/<email>', methods=['GET', 'POST'])
def adminRequestInteraction(email):
    if request.method=='POST':
        approval = request.form['interact']

        if approval=="accept":
            updateBuyerToSeller(email)
            flash('Approved request of buyer to become seller!',category="success")
            return redirect(url_for('homepage.homeAdmin'))
        elif approval=="decline":
            rejectBuyerToSeller(email)
            flash('Declined request of buyer to become seller!',category="error")
            return redirect(url_for('homepage.homeAdmin'))
        
    return render_template('admin/home_admin.html', accountEmail=email)

# methods ----------------------------------------------------------------------------------------------
def updateBuyerToSeller(email: str):
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.homeAdmin'))
    
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
        return redirect(url_for('homepage.homeAdmin'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f'UPDATE requests SET requestArchived=1 WHERE accountEmail="{email}"')
    '''
        FIXME: WONT UPDATE SHIT
        FIXED: NEED FOR DB TO COMMIT LOL FUCK ME SHIT WAS SO BASIC XDDD
    '''
    conn.commit()
    cursor.close()

def isProfileAndSellerEstablished():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    print(session['accountID'])
    
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM profiles_buyer WHERE accountID={session['accountID']}")
    profileRow = cursor.fetchone()
    print(profileRow)

    if profileRow:
        try:
            cursor.execute("SELECT * FROM address_book WHERE accountID=%s AND profileID=%s", (session['accountID'], profileRow[0]))
            addressBookRow = cursor.fetchone()
            if addressBookRow:
                return "both"
            else:
                return "one"
        except Error as e:
            flash(f'{e}', category='error')
            return redirect(url_for('homepage.home'))
        finally:
            cursor.close()
            conn.close()

    return "none" 