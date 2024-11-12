from . import seller
from flask import render_template, redirect, url_for, flash, session, request
from awesomers.users.routes import logout
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import pathlib

dateNow = datetime.now()

# renders ----------------------------------------------------------------------------------------------
@seller.route('/sellerCenter')
def sellerCenter():
    return render_template('seller/base.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/products')
def products():
    return render_template('seller/products.html', legend="Add product", purpose="renderProducts" , id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/inventory')
def inventory():
    accountID = session['accountID']
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION LOL", category='error')
        return redirect(url_for('seller.inventory'))
    
    cursor = conn.cursor()

    try:
        cursor.execute(f'SELECT * FROM products WHERE accountID={accountID}')
        rows=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('seller/inventory.html', legend="Inventory", purpose="renderInventory", products=rows, id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
    except:
        flash('Could not fetch products from database!', category='error')
        return redirect(url_for('seller.sellerCenter'))

# functions ----------------------------------------------------------------------------------------------
@seller.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    if request.method=='POST':
        accountID = session['accountID']
        productImg = request.files['productImg']
        productName = request.form['productName']
        productDescription = request.form['productDescription']
        productCategory = request.form['productCategory']
        productVariation = request.form['productVariation']
        productQuantity = request.form['productQuantity']
        productPrice = request.form['productPrice']
        productDate = dateNow
        productIsArchived = 0

    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('seller.products'))

    destination = os.path.join('awesomers/static/imgs', productImg.filename)
    productImg.save(secure_filename(productImg.filename))
    print(destination)
    url = productImg.filename

    cursor=conn.cursor()

    try:
        cursor.execute('INSERT INTO products (accountID, img, productName, description, category, variation, price, quantity, dateAdded, isArchived) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (accountID, url, productName, productDescription, productCategory, productVariation, productPrice, productQuantity, productDate, productIsArchived))
        conn.commit()
        flash('Product added successfully!', category='success')
    except mysql.connector.IntegrityError:
        conn.rollback()
        flash('Product already exists!', category='error')
        return redirect(url_for('seller.products'))
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('seller.products'))

def insertImage(filePath):
    with open(filePath, "rb") as File:
        imageData = File.read() 
    return imageData