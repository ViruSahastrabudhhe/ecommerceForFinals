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

@profiles.route('/buyerProfile')
def buyerProfile():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM profiles_buyer WHERE accountID={session['accountID']}")
    profileRow = cursor.fetchone()

    if profileRow is None:
        return render_template('homepage/buyer/profile_buyer.html', legend="Profile", isProfile="false", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

    try:
        # path=("awesomers/static/imgs/")
        # filePath = os.path.dirname(path)
        # print(filePath)
        pictureFile = profileRow[3].decode(encoding="utf-8")
        # relativePath = pictureFile
        # print(relativePath)
        # absoluteFilePath = os.path.join(filePath, relativePath)
        # print(absoluteFilePath)
        # with open(absoluteFilePath, "rb") as f:
        #     text = f.read()
        return render_template('homepage/buyer/profile_buyer.html', legend="Profile", isProfile="true", profilePicture=pictureFile, profileInfo=profileRow, id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
    except Error as e:
        flash(f"{e}", category='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()

@profiles.route('/addBuyerProfile', methods=['GET', 'POST'])
def addBuyerProfile():
    dateNow = datetime.now()

    accountID = session['accountID']
    buyerName = request.form['usernameAddPr']
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
        picName = str(uuid.uuid1()) + "_" + picFilename
        buyerPicture.save(os.path.join("awesomers/static/imgs", picName))
        buyerPicture = picName

        try:
            sql = "INSERT INTO profiles_buyer (accountID, buyerName, buyerPicture, buyerPhoneNum, buyerCountry, buyerDateCreated, isArchived) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = accountID, buyerName, buyerPicture, buyerPhoneNum, buyerCountry, buyerDateCreated, buyerIsArchived
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
        buyerUsername = request.form['usernameEditPr']
        buyerPhoneNum = request.form['phoneNumEditPr']
        buyerCountry = request.form['countryEditPr']
        buyerPicture = request.files['pictureEditPr']
        buyerDateEdited = dateEdited

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('profiles.buyerProfile'))
        
        cursor = conn.cursor()

        picFilename = secure_filename(buyerPicture.filename)
        picName = str(uuid.uuid1()) + "_" + picFilename
        buyerPicture.save(os.path.join("awesomers/static/imgs", picName))
        buyerPicture = picName

        try:
            sql = "UPDATE profiles_buyer SET buyerName=%s AND buyerPhoneNum=%s and buyerCountry=%s and buyerPicture=%s AND buyerDateEdited=%s WHERE accountID=%s"
            val = buyerUsername, buyerPhoneNum, buyerCountry, buyerPicture, buyerDateEdited, session['accountID']
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