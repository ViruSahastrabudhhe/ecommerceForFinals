from . import seller
from awesomers import app
from flask import render_template, redirect, url_for, flash, session, request
from awesomers.users.routes import logout
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid as uuid
import os

app.config['UPLOAD_FOLDER'] = "awesomers/static/imgs"
dateNow = datetime.now()

# renders ----------------------------------------------------------------------------------------------
@seller.route('/sellerCenter')
def sellerCenter():
    return render_template('seller/seller_center.html', legend="Dashboard", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/renderProductManagement')
def renderProductManagement():
    accountID = session['accountID']
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION LOL", category='error')
        return redirect(url_for('seller.sellerCenter'))
    
    cursor = conn.cursor()

    try:
        cursor.execute(f'SELECT * FROM products WHERE accountID={accountID} AND isArchived=0')
        rows=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('seller/product_management.html', legend="Product management", purpose="manageProducts", activeSubmenu="productManagement", products=rows, id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
    except:
        flash('Could not fetch products from database!', category='error')
        return redirect(url_for('seller.sellerCenter'))

@seller.route('/renderAddProducts')
def renderAddProducts():
    return render_template('seller/add_products.html', legend="Add products", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/renderOrders')
def renderOrders():
    return render_template('seller/orders.html', legend="Orders", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/renderReturns')
def renderReturns():
    return render_template('seller/returns.html', legend="Returns", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/renderReviews')
def renderReviews():
    return render_template('seller/reviews.html', legend="Reviews", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/sellerBase')
def sellerBase():
    return render_template('oldSeller/base.html', legend="Base", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/products')
def products():
    return render_template('oldSeller/products.html', legend="Add product", purpose="renderProducts" , id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/inventory')
def inventory():
    accountID = session['accountID']
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION LOL", category='error')
        return redirect(url_for('seller.sellerCenter'))
    
    cursor = conn.cursor()

    try:
        cursor.execute(f'SELECT * FROM products WHERE accountID={accountID}')
        rows=cursor.fetchall()
        return render_template('oldSeller/inventory.html', legend="Inventory", purpose="renderInventory", products=rows, id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
    except:
        flash('Could not fetch products from database!', category='error')
        return redirect(url_for('seller.inventory'))
    finally:
        cursor.close()
        conn.close()

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
        return redirect(url_for('seller.renderAddProducts'))

    cursor=conn.cursor()

    picFilename = secure_filename(productImg.filename)
    picName = str(uuid.uuid1()) + "_" + picFilename
    # productImg.save(os.path.join(app.config['UPLOAD_FOLDER']), picName)
    productImg = picName

    try:
        cursor.execute('INSERT INTO products (accountID, picture, productName, description, category, variation, price, quantity, dateAdded, isArchived) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (accountID, productImg, productName, productDescription, productCategory, productVariation, productPrice, productQuantity, productDate, productIsArchived))
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

# @seller.route('/editProducts/', methods=['GET', 'POST'])
# def editProducts():
#     if request.method=="POST":
#         accountID = request.args.get(session['accountID'])
#         productID = request.args.get(session['productID'])
#         productName = request.form['productName']
#         productPrice = request.form['productPrice']
#         productQuantity = request.form['productQuantity']
        
# @seller.route('/deleteProduct/<productID>', methods=['GET', 'POST'])
# def deleteProduct(productID):
#     if request.method=="POST":
#         conn = get_db_connection()
#         if conn is None:
#             flash('NO DB CONNECTION', category='error')
#             return redirect(url_for('seller.sellerCenter'))
        
#         cursor=conn.cursor()

#         try:
#             cursor.execute(f"UPDATE products SET isArchived=1 WHERE productID={productID}")
#             conn.commit()
#             flash('Product deleted!', category='success')
#             return redirect(url_for('seller.renderProductManagement'))
#         except:
#             conn.rollback()
#             flash('Product not deleted!', category='error')
#             return redirect(url_for('seller.renderProductManagement'))
#         finally:
#             cursor.close()
#             conn.close()

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData
