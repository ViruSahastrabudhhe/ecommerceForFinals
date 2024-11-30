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

@seller.route('/seller-center')
def sellerCenter():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('seller/seller_center.html', legend="Dashboard", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/testTemplate')
def testTemplate():
    return render_template('kaiAdmin/index.html')


# store ----------------------------------------------------------------------------------------------
@seller.route('/store-profile')
def renderStoreProfile():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))

    return redirect(url_for('profiles.sellerProfile'))

@seller.route('/store-address')
def renderStoreAddress():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))

    return render_template('seller/store/store_address_book.html', legend="Store address", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])


# products ----------------------------------------------------------------------------------------------
@seller.route('/product-management')
def renderProductManagement():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))

    accountID = session['accountID']
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION LOL", category='error')
        return redirect(url_for('seller.sellerCenter'))
    
    cursor = conn.cursor()

    try:
        cursor.execute(f'SELECT * FROM products WHERE accountID={accountID} AND isArchived=0')
        rows=cursor.fetchall()
        return render_template('seller/products/product_management.html', legend="Product management", products=rows, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        flash(f'{e}', category='error')
        return redirect(url_for('seller.sellerCenter'))
    finally:
        cursor.close()
        conn.close()

@seller.route('/active-products')
def renderActiveProducts():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('kaiAdmin/forms/forms.html')

@seller.route('/add-products')
def renderAddProducts():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))

    return render_template('seller/products/add_products.html', legend="Add products", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/product-management/edit/<productID>')
def renderEditProducts(productID):
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))

    # FIXME: WONT RENDER CSS
    # FIXED: TURN EVERY NON-URL_FOR LINK IN THE INDEX.HTML INTO A URL_FOR
    accountID = session['accountID']
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('seller.sellerCenter'))
    
    cursor=conn.cursor()

    try:
        cursor.execute("SELECT * FROM products WHERE productID=%s AND accountID=%s", (productID, accountID))
        rows=cursor.fetchall()
        return render_template('seller/products/edit_products.html', legend="Edit products", productToBeEdited=rows, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        flash(f"{e}", category='error')
        return redirect(url_for('seller.sellerCenter'))
    finally:
        cursor.close()
        conn.close()

@seller.route('/archived-products')
def renderArchivedProducts():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))

    conn = get_db_connection()

    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('seller.sellerCenter'))
    
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM products WHERE isArchived=1")
        rows=cursor.fetchall()
        return render_template('seller/products/archived_products.html', legend="Archived products", archivedProducts=rows, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except:
        flash('Could not fetch products from database!', category='error')
        return redirect(url_for('seller.sellerCenter'))
    finally:
        cursor.close()
        conn.close()


# orders ----------------------------------------------------------------------------------------------
@seller.route('/orders')
def renderOrders():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('seller/orders/orders.html', legend="Orders", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/returns')
def renderReturns():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('seller/orders/returns.html', legend="Returns", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/reviews')
def renderReviews():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('seller/orders/reviews.html', legend="Reviews", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])


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
        productBrand = request.form['productBrand']
        productDescription = request.form['productDescription']
        productCategory = request.form['productCategory']
        productVariation = request.form['productVariation']
        productQuantity = request.form['productQuantity']
        productPrice = request.form['productPrice']
        productDate = dateNow
        productIsArchived = 0
        productIsActive = 0

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

        cursor.execute(f"SELECT * FROM products WHERE productName='{productName}'")
        item = cursor.fetchone()

        if item:
            flash("Product already exists!", category='error')
            cursor.close()
            conn.close()
            return redirect(url_for('seller.renderAddProducts'))

        if interact=="addProduct":
            try:
                sql = "INSERT INTO products (accountID, picture, productName, brand, description, category, variation, price, quantity, dateAdded, isActive, isArchived) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                # for img in productImgs:
                    # val.append((accountID, img, productName, productDescription, productCategory, productVariation, productPrice, productQuantity, productDate, productIsArchived))
                val = accountID, productImg, productName, productBrand, productDescription, productCategory, productVariation, productPrice, productQuantity, productDate, productIsActive, productIsArchived
                cursor.execute(sql, val)
                conn.commit()
                flash('Product added successfully!', category='success')
                return redirect(url_for('seller.renderAddProducts'))
            except Error as e:
                conn.rollback()
                flash(f'{e}', category='error')
                return redirect(url_for('seller.renderAddProducts'))
            finally:
                cursor.close()
                conn.close()

    return redirect(url_for('seller.renderAddProducts'))

@seller.route('/editProduct/<productID>', methods=['GET', 'POST'])
def editProduct(productID):
    dateEdited = datetime.now()

    if request.method=="POST":
        interact = request.form['submitButton']
        accountID = session['accountID']
        productImg = request.files['productImg']
        productName = request.form['productName']
        productBrand = request.form['productBrand']
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
        productImg.save(os.path.join("awesomers/static/imgs", picName))
        productImg = picName

        if interact=='editProduct':
            try:
                sql = "UPDATE products SET picture=%s, productName=%s, brand=%s, description=%s, category=%s, variation=%s, price=%s, quantity=%s, dateEdited=%s WHERE productID=%s AND accountID=%s"
                val = productImg, productName, productBrand, productDescription, productCategory, productVariation, productPrice, productQuantity, dateEdited, productID, accountID
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

@seller.route('/productActivation/<productID>', methods=['GET', 'POST'])
def productActivation(productID):
    if request.method=="POST":
        activation=request.form['activationButton']

        conn=get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('seller.sellerCenter'))

        cursor=conn.cursor()

        if activation=="activate":
            try:
                cursor.execute(f"UPDATE products SET isActive=0 WHERE productID={productID}")
                conn.commit()
                flash('Product activated!', category='success')
                return redirect(url_for('seller.renderProductManagement'))
            except:
                conn.rollback()
                flash('Product not activated!', category='error')
                return redirect(url_for('seller.renderProductManagement'))
            finally:
                cursor.close()
                conn.close()

        if activation=="deactivate":
            try:
                cursor.execute(f"UPDATE products SET isActive=1 WHERE productID={productID}")
                conn.commit()
                flash('Product deactivated!', category='success')
            except:
                conn.rollback()
                flash('Product not deactivated!', category='error')
                return redirect(url_for('seller.renderProductManagement'))
            finally:
                cursor.close()
                conn.close()

    return redirect(url_for('seller.renderProductManagement'))

# old seller ----------------------------------------------------------------------------------------------
@seller.route('/sellerBase')
def sellerBase():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('oldSeller/base.html', legend="Base", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/products')
def products():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('oldSeller/products.html', legend="Add product", purpose="renderProducts" , id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/inventory')
def inventory():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    accountID = session['accountID']
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION LOL", category='error')
        return redirect(url_for('seller.sellerCenter'))
    
    cursor = conn.cursor()

    try:
        cursor.execute(f'SELECT * FROM products WHERE accountID={accountID}')
        rows=cursor.fetchall()
        return render_template('oldSeller/inventory.html', legend="Inventory", purpose="renderInventory", products=rows, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except:
        flash('Could not fetch products from database!', category='error')
        return redirect(url_for('seller.inventory'))
    finally:
        cursor.close()
        conn.close()
