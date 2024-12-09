from . import seller
from flask import render_template, redirect, url_for, flash, session, request
from awesomers.orders.routes import getOrderDetailsForSeller, getOrderProductDetailsForSeller, getBuyerNameForSellerOrders, getBuyerAddressForSellerOrders, getBuyerAddressForSellerOrderDetails
from awesomers.users.routes import logout
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection
from datetime import datetime, date
from werkzeug.utils import secure_filename
import uuid as uuid
import pathlib
import os

@seller.route('/seller-center')
def sellerCenter():
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('seller/seller_center.html', legend="Dashboard", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/testTemplate')
def testTemplate():
    return render_template('kaiAdmin/index.html')


# store ----------------------------------------------------------------------------------------------
@seller.route('/store/store-seller')
def renderStoreProfile():
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))

    return redirect(url_for('profiles.sellerProfile'))

@seller.route('/store/store-address')
def renderStoreAddress():
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    if isProfileAndAddressEstablished()=="both":
        profileRow=getStoreProfileRow()
        addressBookRows=getAddressStoreRows()
        return render_template('seller/store/address_store.html', legend="Store address", isAddress='true', isProfile='true', profileInfo=profileRow, addressInfo=addressBookRows, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    elif isProfileAndAddressEstablished()=="profile":
        profileRow=getStoreProfileRow()
        addressBookRows=getAddressStoreRows()
        return render_template('seller/store/address_store.html', legend="Store address", isAddress='false', isProfile='true', profileInfo=profileRow, addressInfo=addressBookRows, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    else:
        profileRow=getStoreProfileRow()
        addressBookRows=getAddressStoreRows()
        return render_template('seller/store/address_store.html', legend="Store address", isAddress='false', isProfile='false', profileInfo=profileRow, addressInfo=addressBookRows, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])


# products ----------------------------------------------------------------------------------------------
@seller.route('/products/product-management')
def renderProductManagement():
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))
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

@seller.route('/products/active-products')
def renderActiveProducts():
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('kaiAdmin/forms/forms.html')

@seller.route('/products/add-products')
def renderAddProducts():
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))

    conn=get_db_connection()
    cursor=conn.cursor()
    sql='SELECT * FROM profiles_seller WHERE accountID=%s'
    val=session['accountID']
    cursor.execute(sql, (val, ))
    sellerProfile=cursor.fetchone()

    return render_template('seller/products/add_products.html', legend="Add products", sellerProfileInfo=sellerProfile, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/products/product-management/edit/<productID>')
def renderEditProducts(productID):
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))

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

@seller.route('/products/archived-products')
def renderArchivedProducts():
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))

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
@seller.route('/seller/orders')
def renderOrders():
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))

    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    sellerProfileID=getStoreProfileRow()
    orderDetails=getOrderDetailsForSeller(sellerProfileID[0])
    orderBuyerDetails=getBuyerNameForSellerOrders(sellerProfileID[0])
    orderBuyerAddressDetails=getBuyerAddressForSellerOrders(sellerProfileID[0])

    return render_template('seller/orders/seller_orders.html', legend="Order history", orderBuyerInfo=orderBuyerDetails, orderBuyerAddressInfo=orderBuyerAddressDetails, orderDetailsInfo=orderDetails, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/seller/order-details/<orderDetailsID>')
def viewSellerOrderDetails(orderDetailsID):
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))

    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    sellerProfileID=getStoreProfileRow()
    orderDetails=getOrderDetailsForSeller(sellerProfileID[0])
    orderItems=getOrderProductDetailsForSeller(orderDetailsID)
    orderBuyerDetails=getBuyerNameForSellerOrders(sellerProfileID[0])
    orderBuyerAddressDetails=getBuyerAddressForSellerOrderDetails(sellerProfileID[0], orderDetailsID)

    return render_template('seller/orders/seller_orders_details.html', legend="Order details", orderItemsInfo=orderItems, orderDetailsID=orderDetailsID, orderBuyerInfo=orderBuyerDetails, orderBuyerAddressInfo=orderBuyerAddressDetails, orderDetailsInfo=orderDetails, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/reviews')
def renderReviews():
    if session['loggedIn'] == False:
        flash('Please login first!', category='error')
        return redirect(url_for('users.landing'))

    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('seller/orders/seller_reviews.html', legend="Reviews", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@seller.route('/returns')
def renderReturns():
    if session['accountRole'] != 'seller':
        flash("You must be a registered seller in order to access this!", category='error')
        return redirect(url_for('homepage.home'))
    
    return render_template('seller/orders/returns.html', legend="Returns", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])


# product functions ----------------------------------------------------------------------------------------------
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
        picName = str(session['accountID']) + "_" + picFilename
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
        picName = str(session['accountID']) + "_" + picFilename
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


# address functions ----------------------------------------------------------------------------------------------
@seller.route('/store/store-address/add-address', methods=['GET', 'POST'])
def addStoreAddress():
    dateNow = datetime.now()
    if request.method=='POST':
        storeName=request.form['nameAddAS']
        country=request.form['countryAddAS']
        province=request.form['provinceAddAS']
        city=request.form['cityAddAS']
        district=request.form['districtAddAS']
        streetName=request.form['streetNameAddAS']
        unitName=request.form['unitNameAddAS']
        postal=request.form['postalAddAS']
        phoneNum=request.form['phoneNumAddAS']
        dateCreated = dateNow

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('homepage.home'))
        
        cursor=conn.cursor()

        try:
            sql = "INSERT INTO address_store (accountID, profileID, storeName, storeCountry, storeProvince, storeCity, storeDistrict, storeStreetName, storeUnitName, storePostal, storePhoneNum, storeDateCreated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val = session['accountID'], getStoreProfileRow()[0], storeName, country, province, city, district, streetName, unitName, postal, phoneNum, dateCreated
            cursor.execute(sql, val)
            conn.commit()
            flash('Successfully added new address!', category='success')
            return redirect(url_for('seller.renderStoreAddress'))
        except Error as e:
            conn.rollback()
            flash(f"{e}!", category='error')
            return redirect(url_for('seller.renderStoreAddress'))
        finally:
            cursor.close()
            conn.close()

@seller.route('/store/store-address/edit-address', methods=['GET', 'POST'])
def editStoreAddress():
    dateNow = datetime.now()
    if request.method=='POST':
        storeName=request.form['nameEditAS']
        country=request.form['countryEditAS']
        province=request.form['provinceEditAS']
        city=request.form['cityEditAS']
        district=request.form['districtEditAS']
        streetName=request.form['streetNameEditAS']
        unitName=request.form['unitNameEditAS']
        postal=request.form['postalEditAS']
        phoneNum=request.form['phoneNumEditAS']
        dateEdited = dateNow

        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('homepage.home'))
        
        cursor=conn.cursor()

        try:
            sql = "UPDATE address_store SET storeName=%s, storeCountry=%s, storeProvince=%s, storeCity=%s, storeDistrict=%s, storeStreetName=%s, storeUnitName=%s, storePostal=%s, storePhoneNum=%s, storeDateEdited=%s WHERE accountID=%s AND profileID=%s"
            val = storeName, country, province, city, district, streetName, unitName, postal, phoneNum, dateEdited, session['accountID'], getStoreProfileRow()[0]
            cursor.execute(sql, val)
            conn.commit()
            flash('Successfully edited address!', category='success')
            return redirect(url_for('seller.renderStoreAddress'))
        except Error as e:
            conn.rollback()
            flash(f"{e}!", category='error')
            return redirect(url_for('seller.renderStoreAddress'))
        finally:
            cursor.close()
            conn.close()

@seller.route('/store/store-address/delete-address', methods=['GET', 'POST'])
def deleteStoreAddress():
    if request.method=='POST':
        conn = get_db_connection()
        if conn is None:
            flash('NO DB CONNECTION', category='error')
            return redirect(url_for('homepage.home'))
        
        cursor=conn.cursor()

        try:
            sql = "DELETE FROM address_store WHERE accountID=%s AND profileID=%s"
            val = session['accountID'], getStoreProfileRow()[0]
            cursor.execute(sql, val)
            conn.commit()
            flash('Successfully deleted address!', category='success')
            return redirect(url_for('seller.renderStoreAddress'))
        except Error as e:
            conn.rollback()
            flash(f"{e}!", category='error')
            return redirect(url_for('seller.renderStoreAddress'))
        finally:
            cursor.close()
            conn.close()


# misc functions ----------------------------------------------------------------------------------------------
def isProfileAndAddressEstablished():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles_seller WHERE accountID=%s", (session['accountID'], ))
    profileRow = cursor.fetchone()

    if profileRow is None:
        return "none"
    
    cursor.execute("SELECT * FROM address_store WHERE accountID=%s AND profileID=%s", (session['accountID'], profileRow[0]))
    addressBookRow = cursor.fetchone()
    if addressBookRow is None:
        return "profile"
        
    return "both"

def getStoreProfileRow():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles_seller WHERE accountID=%s", (session['accountID'], ))
    profileRow = cursor.fetchone()

    if profileRow is None:
        return "none"

    return profileRow

def getAddressStoreRows():
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM address_store WHERE accountID=%s AND profileID=%s", (session['accountID'], getStoreProfileRow()[0]))
    addressBookRow = cursor.fetchone()

    if addressBookRow is None:
        return "none"

    return addressBookRow


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