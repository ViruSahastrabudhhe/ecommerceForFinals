from . import seller
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
@seller.route('/sellerCenter')
def sellerCenter():
    return render_template('seller/seller_center.html', legend="Dashboard", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/testTemplate')
def testTemplate():
    return render_template('kaiAdmin/index.html')

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
        return render_template('seller/product_management.html', legend="Product management", products=rows, id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
    except Error as e:
        flash(f'{e}', category='error')
        return redirect(url_for('seller.sellerCenter'))
    finally:
        cursor.close()
        conn.close()

@seller.route('/renderAddProducts')
def renderAddProducts():
    return render_template('seller/add_products.html', legend="Add products", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@seller.route('/renderEditProducts/<productID>')
def renderEditProducts(productID):
    # FIXME: WONT RENDER CSS
    accountID = session['accountID']
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('seller.sellerCenter'))
    
    cursor=conn.cursor()

    try:
        cursor.execute("SELECT * FROM products WHERE productID=%s AND accountID=%s", (productID, accountID))
        rows=cursor.fetchall()
        return render_template('seller/edit_products.html', legend="Edit products", productToBeEdited=rows, id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
    except Error as e:
        flash(f"{e}", category='error')
        return redirect(url_for('seller.sellerCenter'))
    finally:
        cursor.close()
        conn.close()

@seller.route('/renderArchivedProducts')
def renderArchivedProducts():
    conn = get_db_connection()

    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('seller.sellerCenter'))
    
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM products WHERE isArchived=1")
        rows=cursor.fetchall()
        return render_template('seller/archived_products.html', legend="Archived products", archivedProducts=rows, id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
    except:
        flash('Could not fetch products from database!', category='error')
        return redirect(url_for('seller.sellerCenter'))
    finally:
        cursor.close()
        conn.close()

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
    dateNow = datetime.now()

    if request.method=='POST':
        # listOfProductImages = []
        interact = request.form['submitButton']
        accountID = session['accountID']
        # productImgs = request.files.getlist('productImg')
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

        # for productImg in productImgs:
        picFilename = secure_filename(productImg.filename)
        picName = str(uuid.uuid1()) + "_" + picFilename
        productImg.save(os.path.join("awesomers/static/imgs", picName))
        productImg = picName
            # listOfProductImages.append(productImg)

        if interact=="addProduct":
            try:
                sql = "INSERT INTO products (accountID, picture, productName, description, category, variation, price, quantity, dateAdded, isArchived) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                # for img in productImgs:
                    # val.append((accountID, img, productName, productDescription, productCategory, productVariation, productPrice, productQuantity, productDate, productIsArchived))
                val = accountID, productImg, productName, productDescription, productCategory, productVariation, productPrice, productQuantity, productDate, productIsArchived
                cursor.execute(sql, val)
                conn.commit()
                flash('Product added successfully!', category='success')
                return redirect(url_for('seller.renderAddProducts'))
            except mysql.connector.IntegrityError:
                conn.rollback()
                flash('Product already exists!', category='error')
                return redirect(url_for('seller.renderAddProducts'))
            finally:
                cursor.close()
                conn.close()

    return redirect(url_for('seller.renderAddProducts'))

@seller.route('/editProduct/<productID>', methods=['GET', 'POST'])
def editProduct(productID):
    if request.method=="POST":
        interact = request.form['submitButton']
        accountID = session['accountID']
        productImg = request.files['productImg']
        productName = request.form['productName']
        productDescription = request.form['productDescription']
        productCategory = request.form['productCategory']
        productVariation = request.form['productVariation']
        productQuantity = request.form['productQuantity']
        productPrice = request.form['productPrice']

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION LOL", category='error')
            return redirect(url_for('seller.sellerCenter'))
        
        cursor=conn.cursor()

        picFilename = secure_filename(productImg.filename)
        picName = str(uuid.uuid1()) + "_" + picFilename
        # productImg.save(os.path.join("awesomers/static/imgs", picName))
        productImg = picName

        if interact=='editProduct':
            try:
                sql = "UPDATE products SET picture=%s, productName=%s, description=%s, category=%s, variation=%s, price=%s, quantity=%s WHERE productID=%s AND accountID=%s"
                val = productImg, productName, productDescription, productCategory, productVariation, productPrice, productQuantity, productID, accountID
                cursor.execute(sql, val)
                conn.commit()
                flash('Product edited successfully!', category='success')
            except Error as e:
                conn.rollback()
                flash(f'{e}', category='error')
                return redirect(url_for('seller.renderAddProducts'))
            finally:
                cursor.close()
                conn.close()

    return redirect(url_for('seller.renderProductManagement'))
        
@seller.route('/deleteProduct/<productID>', methods=['GET', 'POST'])
def deleteProduct(productID):
    if request.method=="POST":
        archive=request.form['deleteProduct']

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('seller.sellerCenter'))
        
        cursor=conn.cursor()

        if archive=="delete":
            try:
                cursor.execute(f"UPDATE products SET isArchived=1 WHERE productID={productID}")
                conn.commit()
                flash('Product archived!', category='success')
                return redirect(url_for('seller.renderProductManagement'))
            except:
                conn.rollback()
                flash('Product not archived!', category='error')
                return redirect(url_for('seller.renderProductManagement'))
            finally:
                cursor.close()
                conn.close()

@seller.route('/restoreProduct/<productID>', methods=['GET', 'POST'])
def restoreProduct(productID):
    if request.method=="POST":
        restore=request.form['restoreProduct']

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('seller.sellerCenter'))
        
        cursor=conn.cursor()

        if restore=="restore":
            try:
                cursor.execute(f"UPDATE products SET isArchived=0 WHERE productID={productID}")
                conn.commit()
                flash('Product restored!', category='success')
                return redirect(url_for('seller.renderArchivedProducts'))
            except:
                conn.rollback()
                flash('Product not restored!', category='error')
                return redirect(url_for('seller.renderArchivedProducts'))
            finally:
                cursor.close()
                conn.close()

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData
