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
from datetime import datetime

@homepage.route('/home')
def home():
    if session['accountRole']=='seller':
        return render_template('seller/homepage/homepage_seller.html', id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    elif session['accountRole']=='buyer':
        return render_template('homepage/buyer/homepage_buyer.html', id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

# profile ----------------------------------------------------------------------------------------------
@homepage.route('/profile')
def profile():
    if session['accountRole'] == 'buyer':
        return redirect(url_for('profiles.buyerProfile'))
    if session['accountRole'] == 'seller':
        return redirect(url_for('profiles.buyerProfile'))

# buyer seller registration ----------------------------------------------------------------------------------------------
@homepage.route('/seller-registration')
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
@homepage.route('/address-book')
def addressBook():
    if isProfileAndAddressEstablished()=="both":
        profileRows=getBuyerProfileRow()
        addressBookRows=getAddressBookRows()
        addressBookIsDefaultCount=getIsDefaultCountFromAddressBookRows()
        return render_template('homepage/buyer/address_book_buyer.html', legend="Address book", isAddress='true', isProfile='true', profileInfo=profileRows, addressInfo=addressBookRows, isDefaultCount=addressBookIsDefaultCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    elif isProfileAndAddressEstablished()=="profile":
        profileRows=getBuyerProfileRow()
        addressBookRows=getAddressBookRows()
        addressBookIsDefaultCount=getIsDefaultCountFromAddressBookRows()
        return render_template('homepage/buyer/address_book_buyer.html', legend="Address book", isAddress='false', isProfile='true', profileInfo=profileRows, addressInfo=addressBookRows, isDefaultCount=addressBookIsDefaultCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    else:
        profileRows=getBuyerProfileRow()   
        addressBookRows=getAddressBookRows()
        addressBookIsDefaultCount=getIsDefaultCountFromAddressBookRows()
        return render_template('homepage/buyer/address_book_buyer.html', legend="Address book", isAddress='false', isProfile='false', profileInfo=profileRows, addressInfo=addressBookRows, isDefaultCount=addressBookIsDefaultCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@homepage.route('/addressBook/edit/<addressBookID>')
def editAddress(addressBookID):
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM address_book WHERE accountID=%s and addressBookID=%s", (session['accountID'], addressBookID))
    row = cursor.fetchone()

    profileRows=getBuyerProfileRow()
    addressBookRows=getAddressBookRows()
    addressBookIsDefaultCount=getIsDefaultCountFromAddressBookRows()

    if row is None:
        flash("Address does not exist!", category='error')
        return redirect(url_for('homepage.addressBook'))

    try:
        return render_template('homepage/buyer/edit_address_buyer.html', legend="Edit address", isAddress='true', isProfile='true', isDefaultCount=addressBookIsDefaultCount, profileInfo=profileRows, addressInfo=row, addressBookInfo=addressBookRows, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        flash(f"{e}", category='error')
        return redirect(url_for('homepage.addressBook'))
    finally:
        cursor.close()
        conn.close()

@homepage.route('/addBuyerAddress', methods=['GET', 'POST'])
def addBuyerAddress():
    dateNow = datetime.now()
    if request.method=='POST':
        recipientName=request.form['fullNameAddAB']
        country=request.form['countryAddAB']
        province=request.form['provinceAddAB']
        city=request.form['cityAddAB']
        district=request.form['districtAddAB']
        streetName=request.form['streetNameAddAB']
        unitName=request.form['unitAddAB']
        postal=request.form['postalAddAB']
        phoneNum=request.form['phoneNumAddAB']
        category=request.form['categoryAddAB']
        isDefault=request.form.get('isdefaultAddAB')
        dateCreated = dateNow

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('homepage.home'))
        
        profileRow=getBuyerProfileRow()
        cursor=conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM address_book WHERE isDefault=1 AND accountID={session['accountID']} AND profileID={profileRow[0]}")
        count = cursor.fetchone()

        if isDefault is None:
            isDefault=0

        if count==0:
            isDefault=1
        else:
            cursor.execute(f"UPDATE address_book SET isDefault=0 WHERE accountID={session['accountID']} AND profileID={profileRow[0]}")
            conn.commit()

        if isDefault==1:
            cursor.execute(f"UPDATE address_book SET isDefault=0 WHERE accountID={session['accountID']} AND profileID={profileRow[0]}")
            conn.commit()

        try:
            sql = "INSERT INTO address_book (accountID, profileID, recipientName, addressCountry, addressProvince, addressCity, addressDistrict, addressStreetName, addressUnitName, addressPostal, addressPhoneNum, addressCategory, addressDateCreated, isDefault) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val = session['accountID'], getBuyerProfileRow()[0], recipientName, country, province, city, district, streetName, unitName, postal, phoneNum, category, dateCreated, isDefault
            cursor.execute(sql, val)
            conn.commit()
            flash('Added new address!', category='success')
            return redirect(url_for('homepage.addressBook'))
        except Error as e:
            conn.rollback()
            flash(f"{e}!", category='error')
            return redirect(url_for('homepage.addressBook'))
        finally:
            cursor.close()
            conn.close()

@homepage.route('/addressBook/edit/<addressBookID>', methods=['GET', 'POST'])
def editBuyerAddress(addressBookID):
    dateNow = datetime.now()
    if request.method=='POST':
        recipientName=request.form['fullNameEditAB']
        country=request.form['countryEditAB']
        province=request.form['provinceEditAB']
        city=request.form['cityEditAB']
        district=request.form['districtEditAB']
        streetName=request.form['streetNameEditAB']
        unitName=request.form['unitEditAB']
        postal=request.form['postalEditAB']
        phoneNum=request.form['phoneNumEditAB']
        category=request.form['categoryEditAB']
        isDefault=request.form.get('isdefaultEditAB')
        dateEdited = dateNow

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('homepage.home'))
        
        profileRow=getBuyerProfileRow()
        cursor=conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM address_book WHERE isDefault=1 AND accountID={session['accountID']} AND profileID={profileRow[0]}")
        count = cursor.fetchone()

        if isDefault is None:
            isDefault=0

        if count==0:
            isDefault=1

        if isDefault==1:
            cursor.execute(f"UPDATE address_book SET isDefault=0 WHERE accountID={session['accountID']} AND profileID={profileRow[0]}")
            conn.commit()

        # FIXME: DEFAULT ADDRESSES ARE ALL SET TO NOT DEFAULT IF U EDIT IT AND DONT TICK THE SET AS DEFAULT ADDRESS BOX, PREVENT THIS

        try:
            sql = "UPDATE address_book SET recipientName=%s, addressCountry=%s, addressProvince=%s, addressCity=%s, addressDistrict=%s, addressStreetName=%s, addressUnitName=%s, addressPostal=%s, addressPhoneNum=%s, addressCategory=%s, addressDateEdited=%s, isDefault=%s WHERE accountID=%s AND addressBookID=%s"
            val = recipientName, country, province, city, district, streetName, unitName, postal, phoneNum, category, dateEdited, isDefault, session['accountID'], addressBookID
            cursor.execute(sql, val)
            conn.commit()
            flash('Successfully added new address!', category='success')
            return redirect(url_for('homepage.addressBook'))
        except Error as e:
            conn.rollback()
            flash(f"{e}!", category='error')
            return redirect(url_for('homepage.addressBook'))
        finally:
            cursor.close()
            conn.close()

@homepage.route('/deleteBuyerAddress/<addressBookID>', methods=['GET', 'POST'])
def deleteBuyerAddress(addressBookID):
    if request.method=='POST':
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))
        
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM address_book WHERE accountID=%s and addressBookID=%s", (session['accountID'], addressBookID))
            conn.commit()
            flash("Successfully deleted address!", category='success')
            return redirect(url_for('homepage.addressBook'))
        except Error as e:
            conn.rollback()
            flash(f"{e}", category='errpr')
            return redirect(url_for('homepage.addressBook'))
        finally:
            cursor.close()
            conn.close()

# seller ----------------------------------------------------------------------------------------------
@homepage.route("/redirectToSellerCenter")
def redirectToSellerCenter():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return redirect(url_for('seller.sellerCenter'))

@homepage.route("/redirectToSellerBase")
def redirectToSellerBase():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return redirect(url_for('seller.sellerBase'))

# admin ----------------------------------------------------------------------------------------------
@homepage.route('/home-admin')
def homeAdmin():
    if session['accountRole'] != 'admin':
        flash("Unknown request!", category='error')
        return redirect(url_for('homepage.home'))
    
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

def isProfileAndAddressEstablished():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM profiles_buyer WHERE accountID={session['accountID']}")
    profileRow = cursor.fetchone()

    if profileRow is None:
        return "none"
    
    cursor.execute("SELECT * FROM address_book WHERE accountID=%s AND profileID=%s", (session['accountID'], profileRow[0]))
    addressBookRow = cursor.fetchone()
    if addressBookRow is None:
        return "profile"
        
    return "both"

def getBuyerProfileRow():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM profiles_buyer WHERE accountID={session['accountID']}")
    profileRow = cursor.fetchone()

    if profileRow is None:
        return "none"

    return profileRow

def getAddressBookRows():
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM address_book WHERE accountID=%s AND profileID=%s ORDER BY isDefault DESC", (session['accountID'], getBuyerProfileRow()[0]))
    addressBookRow = cursor.fetchall()

    if addressBookRow is None:
        return "none"

    return addressBookRow

def getIsDefaultCountFromAddressBookRows():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    profileRow=getBuyerProfileRow()
    cursor=conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM address_book WHERE isDefault=1 AND accountID={session['accountID']} AND profileID={profileRow[0]}")
    count = cursor.fetchone()

    if count is None:
        return 0
    
    return count