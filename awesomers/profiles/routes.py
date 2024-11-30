from . import profiles
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

# renders ----------------------------------------------------------------------------------------------
@profiles.route('/profile/buyer')
def buyerProfile():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM profiles_buyer WHERE accountID={session['accountID']}")
    profileRow = cursor.fetchone()

    if profileRow is None:
        return render_template('homepage/buyer/profile_buyer.html', legend="Profile", isProfile="false", isAddress="false", profileInfo=profileRow, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

    try:
        # path=("awesomers/static/imgs/")
        # filePath = os.path.dirname(path)
        # print(filePath)
        pictureFile = profileRow[4].decode(encoding="utf-8")
        if getAddressBookRow(profileRow[0])!="none":
            return render_template('homepage/buyer/profile_buyer.html', legend="Profile", isProfile="true", isAddress="true", profilePicture=pictureFile, profileInfo=profileRow, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
        return render_template('homepage/buyer/profile_buyer.html', legend="Profile", isProfile="true", isAddress="false", profilePicture=pictureFile, profileInfo=profileRow, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
        # relativePath = pictureFile
        # print(relativePath)
        # absoluteFilePath = os.path.join(filePath, relativePath)
        # print(absoluteFilePath)
        # with open(absoluteFilePath, "rb") as f:
        #     text = f.read()
    except Error as e:
        flash(f"{e}", category='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()

@profiles.route('/profile/seller')
def sellerProfile():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM profiles_seller WHERE accountID={session['accountID']}")
    profileRow = cursor.fetchone()

    if profileRow is None:
        return render_template('seller/store/store_profile.html', legend="Store profile", isProfile='false', profileInfo=profileRow, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

    try:
        pictureFile = profileRow[3].decode(encoding="utf-8")
        return render_template('seller/store/store_profile.html', legend="Store profile", isProfile='true', profilePicture=pictureFile, profileInfo=profileRow, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        flash(f"{e}", category='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()

# buyers ----------------------------------------------------------------------------------------------
@profiles.route('/addBuyerProfile', methods=['GET', 'POST'])
def addBuyerProfile():
    dateNow = datetime.now()

    accountID = session['accountID']
    buyerFirstName = request.form['fnameAddPr']
    buyerLastName = request.form['lnameAddPr']
    buyerPhoneNum = request.form['phoneNumAddPr']
    buyerCountry = request.form['countryAddPr']
    buyerPicture = request.files['pictureAddPr']
    buyerDateCreated = dateNow
    buyerIsArchived = 0

    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.profile'))
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM profiles_buyer WHERE accountID={session['accountID']}")
        record = cursor.fetchone()

        if record:
            flash('Profile already exists!', category='error')
            return redirect(url_for('homepage.profile'))
        
        picFilename = secure_filename(buyerPicture.filename)
        picName = str(session['accountID']) + "_" + picFilename
        buyerPicture.save(os.path.join("awesomers/static/imgs", picName))
        buyerPicture = picName

        try:
            sql = "INSERT INTO profiles_buyer (accountID, buyerFirstName, buyerLastName, buyerPicture, buyerPhoneNum, buyerCountry, buyerDateCreated, isArchived) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = accountID, buyerFirstName, buyerLastName, buyerPicture, buyerPhoneNum, buyerCountry, buyerDateCreated, buyerIsArchived
            cursor.execute(sql, val)
            conn.commit()
            flash('Created new profile!', category="success")
            return redirect(url_for('homepage.profile'))
        except Error as e:
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('homepage.profile'))
        finally:
            cursor.close()
            conn.close()

@profiles.route('/deleteBuyerProfile', methods=['GET', 'POST'])
def deleteBuyerProfile():
    if request.method=='POST':
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.profile'))
        
        cursor=conn.cursor()

        try:
            cursor.execute(f"DELETE FROM profiles_buyer WHERE accountID={session['accountID']}")
            conn.commit()
            flash("Profile successfully deleted!", category='success')
            return redirect(url_for('homepage.profile'))
        except Error as e:
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('homepage.profile'))
        finally:
            cursor.close()
            conn.close()

@profiles.route('/editBuyerProfile', methods=['GET', 'POST'])
def editBuyerProfile():
    dateEdited = datetime.now()

    if request.method=='POST':
        buyerFirstName = request.form['fnameEditPr']
        buyerLastName = request.form['lnameEditPr']
        buyerPhoneNum = request.form['phoneNumEditPr']
        buyerCountry = request.form['countryEditPr']
        buyerPicture = request.files['pictureEditPr']
        buyerDateEdited = dateEdited

        buyerPictureFilename = secure_filename(buyerPicture.filename)
        buyerModifiedPicture = str(session['accountID']) + "_" + buyerPictureFilename

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('profiles.buyerProfile'))
        
        cursor = conn.cursor()
        sql = "SELECT buyerFirstName, buyerLastName, buyerPicture, buyerCountry, buyerPhoneNum, accountID FROM profiles_buyer WHERE buyerFirstName=%s and buyerLastName=%s and buyerPicture=%s and buyerPhoneNum=%s and buyerCountry=%s and accountID=%s"
        val = buyerFirstName, buyerLastName, buyerModifiedPicture, buyerPhoneNum, buyerCountry, session['accountID']
        cursor.execute(sql, val)
        row = cursor.fetchone()

        picFilename = secure_filename(buyerPicture.filename)
        picName = str(session['accountID']) + "_" + picFilename
        buyerPicture.save(os.path.join("awesomers/static/imgs", picName))
        buyerPicture = picName

        if row:
            flash("No changes were made!", category='warning')
            return redirect(url_for('profiles.buyerProfile'))

        try:
            sql = "UPDATE profiles_buyer SET buyerFirstName=%s, buyerLastName=%s, buyerPhoneNum=%s, buyerCountry=%s, buyerPicture=%s, buyerDateEdited=%s WHERE accountID=%s"
            val = buyerFirstName, buyerLastName, buyerPhoneNum, buyerCountry, buyerPicture, buyerDateEdited, session['accountID']
            cursor.execute(sql, val)
            conn.commit()
            flash('Profile successfully edited!', category='success')
            return redirect(url_for('profiles.buyerProfile'))
        except mysql.connector.IntegrityError as e:
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('profiles.buyerProfile'))
        finally:
            cursor.close()
            conn.close()

# seller ----------------------------------------------------------------------------------------------
@profiles.route('/addSellerProfile', methods=['GET', 'POST'])
def addSellerProfile():
    dateNow = datetime.now()

    accountID = session['accountID']
    storeName = request.form['nameAddPr']
    storePhoneNum = request.form['phoneNumAddPr']
    storeCountry = request.form['countryAddPr']
    storePicture = request.files['pictureAddPr']
    storeDateCreated = dateNow
    storeIsArchived = 0

    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('seller.renderStoreProfile'))
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM profiles_seller WHERE accountID={session['accountID']}")
        record = cursor.fetchone()

        if record:
            flash('Profile already exists!', category='error')
            return redirect(url_for('seller.renderStoreProfile'))
        
        picFilename = secure_filename(storePicture.filename)
        picName = str(session['accountID']) + "_" + picFilename
        storePicture.save(os.path.join("awesomers/static/imgs", picName))
        storePicture = picName

        try:
            sql = "INSERT INTO profiles_seller (accountID, storeName, storePicture, storePhoneNum, storeCountry, storeDateCreated, isArchived) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = accountID, storeName, storePicture, storePhoneNum, storeCountry, storeDateCreated, storeIsArchived
            cursor.execute(sql, val)
            conn.commit()
            flash('Created new profile!', category="success")
            return redirect(url_for('seller.renderStoreProfile'))
        except Error as e:
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('seller.renderStoreProfile'))
        finally:
            cursor.close()
            conn.close()

@profiles.route('/deleteSellerProfile', methods=['GET', 'POST'])
def deleteSellerProfile():
    if request.method=='POST':
        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('seller.renderStoreProfile'))
        
        cursor=conn.cursor()

        try:
            cursor.execute(f"DELETE FROM profiles_seller WHERE accountID={session['accountID']}")
            conn.commit()
            flash("Profile successfully deleted!", category='success')
            return redirect(url_for('seller.renderStoreProfile'))
        except Error as e:
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('seller.renderStoreProfile'))
        finally:
            cursor.close()
            conn.close()

@profiles.route('/editSellerProfile', methods=['GET', 'POST'])
def editSellerProfile():
    dateEdited = datetime.now()

    if request.method=='POST':
        storeName = request.form['nameEditPr']
        storePhoneNum = request.form['phoneNumEditPr']
        storeCountry = request.form['countryEditPr']
        storePicture = request.files['pictureEditPr']
        storeDateEdited = dateEdited

        # check if picture is in db, to prevent no changes to be saved
        storePictureFilename = secure_filename(storePicture.filename)
        storeModifiedPicture = str(session['accountID']) + "_" + storePictureFilename

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('seller.renderStoreProfile'))
        
        cursor = conn.cursor()
        sql = "SELECT storeName, storePicture, storeCountry, storePhoneNum, accountID FROM profiles_seller WHERE storeName=%s and storePicture=%s and storePhoneNum=%s and storeCountry=%s and accountID=%s"
        val = storeName, storeModifiedPicture, storePhoneNum, storeCountry, session['accountID']
        cursor.execute(sql, val)
        row = cursor.fetchone()

        picFilename = secure_filename(storePicture.filename)
        picName = str(session['accountID']) + "_" + picFilename
        storePicture.save(os.path.join("awesomers/static/imgs", picName))
        storePicture = picName

        if row:
            flash("No changes were made!", category='warning')
            return redirect(url_for('seller.renderStoreProfile'))

        try:
            sql = "UPDATE profiles_seller SET storeName=%s, storePhoneNum=%s, storeCountry=%s, storePicture=%s, storeDateEdited=%s WHERE accountID=%s"
            val = storeName, storePhoneNum, storeCountry, storePicture, storeDateEdited, session['accountID']
            cursor.execute(sql, val)
            conn.commit()
            flash('Profile successfully edited!', category='success')
            return redirect(url_for('seller.renderStoreProfile'))
        except mysql.connector.IntegrityError as e:
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('seller.renderStoreProfile'))
        finally:
            cursor.close()
            conn.close()

# methods ----------------------------------------------------------------------------------------------
def getAddressBookRow(profileID):
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM address_book WHERE accountID=%s AND profileID=%s", (session['accountID'], profileID))
    addressBookRow = cursor.fetchone()

    if addressBookRow is None:
        return "none"

    return addressBookRow