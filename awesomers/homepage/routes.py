from . import homepage
from awesomers.products.routes import getWishlist, getAvailableProducts, getAvailableProductPictures, getCart, getCartCount, getCartTotalPrice, getLatestProducts, getLatestProductPictures
from awesomers.orders.routes import getOrderDetails, getOrderProductIDs, getOrderProductDetails, getOrderProductItems
from flask import render_template, redirect, url_for, flash, session, request
from awesomers.users.routes import logout
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection
from datetime import datetime, date
from werkzeug.utils import secure_filename
import uuid as uuid
import pathlib
import os

@homepage.route('/home')
def home():
    if session['accountRole']=='seller':
        availableProductsRows=getAvailableProducts()
        availableProductsPicturesRows=getAvailableProductPictures()
        latestProductsRows=getLatestProducts()
        latestProductsPicturesRows=getLatestProductPictures()
        cartRows = getCart()
        cartCount = getCartCount()
        cartSum = getCartTotalPrice()
        wishlist=getWishlist()
        return render_template('seller/homepage/homepage_seller.html', wishlistInfo=wishlist, availableProducts=availableProductsRows, productPictureInfo=availableProductsPicturesRows, latestProductsInfo=latestProductsRows, latestProductsPicturesInfo=latestProductsPicturesRows, cartSumInfo=cartSum, cartInfo=cartRows, cartCountInfo=cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    elif session['accountRole']=='buyer':
        availableProductsRows=getAvailableProducts()
        availableProductsPicturesRows=getAvailableProductPictures()
        latestProductsRows=getLatestProducts()
        latestProductsPicturesRows=getLatestProductPictures()
        cartRows=getCart()
        cartCount=getCartCount()
        cartSum=getCartTotalPrice()
        wishlist=getWishlist()
        return render_template('homepage/buyer/homepage_buyer.html',  wishlistInfo=wishlist, productInfo=availableProductsRows, productPictureInfo=availableProductsPicturesRows, latestProductsInfo=latestProductsRows, latestProductsPicturesInfo=latestProductsPicturesRows, cartSumInfo=cartSum, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@homepage.route('/dashboard')
def viewDashboard():
    if session['loggedIn']==False:
        flash("Please login first!", category='error')
        return redirect(url_for('users.landing'))
    
    cartRows=getCart()
    cartCount=getCartCount()
    cartSum=getCartTotalPrice()
    wishlist=getWishlist()
    orderDetails=getOrderDetails()
    orderProductIDs=getOrderProductIDs()
    orderProductDetails=getOrderProductItems()
    return render_template('homepage/buyer/dashboard_buyer.html', legend='Dashboard', wishlistInfo=wishlist, orderProductDetailsInfo=orderProductDetails, orderProductIDsInfo=orderProductIDs, orderDetailsInfo=orderDetails, cartSumInfo=cartSum, cartInfo=cartRows, cartCountInfo=cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])


# profile ----------------------------------------------------------------------------------------------
@homepage.route('/profile')
def profile():
    if session['loggedIn']==False:
        flash("Please login first!", category='error')
        return redirect(url_for('users.landing'))
    
    if session['accountRole'] == 'buyer':
        return redirect(url_for('profiles.buyerProfile'))
    if session['accountRole'] == 'seller':
        return redirect(url_for('profiles.buyerProfile'))


# buyer seller registration ----------------------------------------------------------------------------------------------
@homepage.route('/seller-registration')
def sellerRegistration():
    if session['loggedIn']==False:
        flash("Please login first!", category='error')
        return redirect(url_for('users.landing'))
    
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    sql = "SELECT * FROM requests WHERE accountID=%s and accountEmail=%s"
    val = session['accountID'], session['accountEmail']
    cursor.execute(sql, val)
    requestRow = cursor.fetchone()
    cartRows=getCart()
    cartCount = getCartCount()
    cartTotal=getCartTotalPrice()
    wishlist=getWishlist()

    if requestRow:
        validIDPictureFile = requestRow[6].decode(encoding="utf-8")
        bankDocumentPictureFile = requestRow[10].decode(encoding="utf-8")
        return render_template('homepage/buyer/seller_registration.html', legend="Seller registration", isRequest='true', wishlistInfo=wishlist, requestInfo=requestRow, validIDPicture=validIDPictureFile, bankDocumentPicture=bankDocumentPictureFile, cartSumInfo=cartTotal, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

    try:
        cursor.execute(f"SELECT * FROM accounts WHERE accountID={session['accountID']}")
        row=cursor.fetchone()
        return render_template('homepage/buyer/seller_registration.html', legend="Seller registration", isRequest='false', wishlistInfo=wishlist, accountInfo=row, cartSumInfo=cartTotal, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
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
    if session['loggedIn']==False:
        flash("Please login first!", category='error')
        return redirect(url_for('users.landing'))

    if isProfileAndAddressEstablished()=="both":
        profileRows=getBuyerProfileRow()
        addressBookRows=getAddressBookRows()
        addressBookIsDefaultCount=getIsDefaultCountFromAddressBookRows()
        cartRows=getCart()
        cartCount = getCartCount()
        cartTotal=getCartTotalPrice()
        wishlist=getWishlist()

        return render_template('homepage/buyer/address_book_buyer.html', legend="Address book", isAddress='true', isProfile='true', wishlistInfo=wishlist, profileInfo=profileRows, addressInfo=addressBookRows, isDefaultCount=addressBookIsDefaultCount, cartSumInfo=cartTotal, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    elif isProfileAndAddressEstablished()=="profile":
        profileRows=getBuyerProfileRow()
        addressBookRows=getAddressBookRows()
        addressBookIsDefaultCount=getIsDefaultCountFromAddressBookRows()
        cartRows=getCart()
        cartCount = getCartCount()
        cartTotal=getCartTotalPrice()
        wishlist=getWishlist()
        return render_template('homepage/buyer/address_book_buyer.html', legend="Address book", isAddress='false', isProfile='true', wishlistInfo=wishlist, profileInfo=profileRows, addressInfo=addressBookRows, isDefaultCount=addressBookIsDefaultCount, cartSumInfo=cartTotal, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    else:
        profileRows=getBuyerProfileRow()   
        addressBookRows=getAddressBookRows()
        addressBookIsDefaultCount=getIsDefaultCountFromAddressBookRows()
        cartRows=getCart()
        cartCount = getCartCount()
        cartTotal=getCartTotalPrice()
        wishlist=getWishlist()
        return render_template('homepage/buyer/address_book_buyer.html', legend="Address book", isAddress='false', isProfile='false', wishlistInfo=wishlist, profileInfo=profileRows, addressInfo=addressBookRows, isDefaultCount=addressBookIsDefaultCount, cartSumInfo=cartTotal, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@homepage.route('/address-book/edit/<addressBookID>')
def editAddress(addressBookID):
    if session['loggedIn']==False:
        flash("Please login first!", category='error')
        return redirect(url_for('users.landing'))
    
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
    cartRows=getCart()
    cartCount = getCartCount()
    cartTotal=getCartTotalPrice()
    wishlist=getWishlist()

    if row is None:
        flash("Address does not exist!", category='error')
        return redirect(url_for('homepage.addressBook'))

    try:
        return render_template('homepage/buyer/edit_address_buyer.html', legend="Edit address", isAddress='true', isProfile='true', wishlistInfo=wishlist, isDefaultCount=addressBookIsDefaultCount, profileInfo=profileRows, addressInfo=row, addressBookInfo=addressBookRows, cartSumInfo=cartTotal, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
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
        return redirect(url_for('users.landing'))
    
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('users.loginAdmin'))   

    return render_template('admin/home_admin.html', legend="Dashboard", email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@homepage.route('/admin/seller-registration')
def viewAdminSellerRequests():
    if session['accountRole'] != 'admin':
        flash("Unknown request!", category='error')
        return redirect(url_for('users.landing'))
    
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('users.loginAdmin'))   

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM requests WHERE requestArchived=0")
        rows=cursor.fetchall()
        return render_template('admin/powers/seller_requests.html', legend="Seller requests", requestsInfo=rows, email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        flash(f'{e}', category='error')
        logout()
    finally:
        cursor.close()
        conn.close()

@homepage.route('/admin/sellers-list')
def viewAdminSellersList():
    if session['accountRole'] != 'admin':
        flash("Unknown request!", category='error')
        return redirect(url_for('users.landing'))
    
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('users.loginAdmin'))   

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT profiles_seller.`sellerProfileID`, profiles_seller.`accountID`, profiles_seller.`storeName`, profiles_seller.`storePhoneNum`, profiles_seller.`storeCountry`, profiles_seller.`storeDateCreated`, accounts.`accountEmail`, accounts.`accountFirstName`, accounts.`accountLastName` FROM profiles_seller JOIN accounts ON profiles_seller.`accountID`=accounts.`accountID`")
        rows=cursor.fetchall()
        return render_template('admin/powers/seller_list.html', legend="Sellers", sellersInfo=rows, email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        flash(f'{e}', category='error')
        logout()
    finally:
        cursor.close()
        conn.close()

@homepage.route('/admin/orders-list')
def viewAdminOrdersList():
    if session['accountRole'] != 'admin':
        flash("Unknown request!", category='error')
        return redirect(url_for('users.landing'))
    
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('users.loginAdmin'))   

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM requests WHERE requestArchived=0")
        rows=cursor.fetchall()
        return render_template('admin/powers/orders_list.html', legend="Orders",  dbhtml=rows, email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        flash(f'{e}', category='error')
        logout()
    finally:
        cursor.close()
        conn.close()

@homepage.route('/admin/products-list')
def viewAdminProductsList():
    if session['accountRole'] != 'admin':
        flash("Unknown request!", category='error')
        return redirect(url_for('users.landing'))
    
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('users.loginAdmin'))   

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM requests WHERE requestArchived=0")
        rows=cursor.fetchall()
        return render_template('admin/powers/products_list.html', legend="Products",  dbhtml=rows, email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
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

def getOrderAddressBookRow():
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    sql = 'SELECT * FROM address_book JOIN order_details ON address_book.`addressBookID`=order_details.`buyerAddressID` WHERE address_book.`accountID`=%s'
    val = session['accountID']
    cursor.execute(sql (val, ))
    addressBookRow = cursor.fetchone()

    return addressBookRow

def getIsDefaultCountFromAddressBookRows():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    profileRow=getBuyerProfileRow()
    cursor=conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM address_book WHERE isDefault=1 AND accountID={session['accountID']}")
    count = cursor.fetchone()

    if count is None:
        return 0
    
    return count

def getBuyerAddressIDs():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect('users.landing')
    
    cursor=conn.cursor()

    sql = 'SELECT buyerAddressID FROM order_details WHERE accountID=%s'
    val = session['accountID']
    cursor.execute(sql, val)
    row=cursor.fetchone()
    results = [i[0] for i in row]

    return results

def getBuyerAddressInfoFromOrderDetails(buyerAddressID):
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect('users.landing')
    
    cursor=conn.cursor()

    sql = "SELECT * FROM address_book JOIN order_details ON address_book.`addressBookID`=order_details.`buyerAddressID` WHERE order_details.`accountID`=%s AND order_details.`buyerAddressID`=%s"
    val = session['accountID'], buyerAddressID
    cursor.execute(sql, val)
    row=cursor.fetchone()

    return row