from . import products
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

# renders ----------------------------------------------------------------------------------------------
@products.route('/product-info/<productID>')
def viewProductPage(productID):
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    productRows=getProducts()
    productRowPictures=getProductPictures()
    cartRows=getCart()
    cartCount = getCartCount()
    storeName=getStoreName()

    try:
        cursor.execute(f'SELECT * FROM products WHERE productID={productID}')
        row=cursor.fetchone()
        pictureFile = row[2].decode(encoding='utf-8')
        return render_template('products/product_info.html', legend="Product information", productIDInfo=row, productIDPicture=pictureFile, productInfo=productRows, productPictureInfo=productRowPictures, storeNameInfo=storeName, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        flash(f"{e}", category='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()

@products.route('/checkout')
def viewCheckout():
    if session['loggedIn']==False:
        flash('Login first, boss!', category='error')
        return redirect(url_for('users.landing'))

    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION!', category='error')
        return redirect(url_for('users.landing'))
    
    productRows=getProducts()
    productRowPictures=getProductPictures()
    cartRows=getCart()
    cartPicturesRows=getCartPictures()
    cartCount = getCartCount()
    cartSum =getCartSum()
    storeName=getStoreName()
    addressBookRows=getAddressBookRows()

    if getAddressBookRows()=='none':
        return render_template('products/checkout.html', productInfo=productRows, productPictureInfo=productRowPictures, storeNameInfo=storeName, addressBookInfo=addressBookRows, cartInfo=cartRows, cartPicturesInfo=cartPicturesRows, cartCountInfo = cartCount, cartSumInfo=cartSum, isAddress='false', legend="Checkout", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    return render_template('products/checkout.html', productInfo=productRows, productPictureInfo=productRowPictures, storeNameInfo=storeName, addressBookInfo=addressBookRows, cartInfo=cartRows, cartPicturesInfo=cartPicturesRows, cartCountInfo = cartCount, cartSumInfo=cartSum, isAddress='true', legend="Checkout", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

# cart functions ----------------------------------------------------------------------------------------------
def getCart():
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute(f"SELECT products.`productName`, cart.`cartQuantity`, products.`price`, cart.`productID` FROM products JOIN cart ON products.`productID` = cart.`productID` WHERE cart.`accountID`={session['accountID']}")
    cartRows=cursor.fetchall()

    return cartRows

def getCartPictures():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))

    cursor = conn.cursor() 
    cursor.execute(f'SELECT * FROM products JOIN cart ON products.`productID` = cart.`productID` WHERE cart.`accountID`={session['accountID']}')
    rows=cursor.fetchall()
    pictureFiles=[]

    for row in rows:
        pictureFile=row[2].decode(encoding='utf-8')
        pictureFiles.append(pictureFile)

    return pictureFiles

@products.route('/cart/add-to-cart/<productID>', methods=['GET', 'POST'])
def addToCart(productID):
    if request.method=='POST':
        accountID = session['accountID']
        cartQuantity = request.form['cartQuantity']

        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))
        
        cursor=conn.cursor()
        cursor.execute(f"SELECT productID FROM cart WHERE productID={productID} AND accountID={session['accountID']}")
        isRowInCart = cursor.fetchone()

        if isRowInCart:
            sql = "UPDATE cart SET cartQuantity=cartQuantity+1 WHERE productID=%s AND accountID=%s"
            val = productID, accountID
            cursor.execute(sql, val)
            conn.commit()
            flash("Successfully added product to cart!", category='success')
            return redirect(url_for('homepage.home'))
        
        try:
            sql = "INSERT INTO cart (accountID, productID, cartQuantity) VALUES (%s, %s, %s)"
            val = accountID, productID, cartQuantity
            cursor.execute(sql, val)
            conn.commit()
            # sql1 = "UPDATE products SET stock=stock-%s WHERE productID=%s"
            # val1 = cartQuantity, productID
            # conn.commit()
            flash("Successfully added product to cart!", category='success')
            return redirect(url_for('homepage.home'))
        except Error as e:
            flash(f"{e}", category='error')
            return redirect(url_for('homepage.home'))
        finally:
            cursor.close()
            conn.close()

@products.route('/cart/clear-cart', methods=['GET', 'POST'])
def clearCart():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute(f"DELETE FROM cart WHERE accountID={session['accountID']}")
    conn.commit()
    flash("Cart contents cleared!", category='success')
    return redirect(url_for('homepage.home'))

def getCartCount():
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute(f"SELECT SUM(cartQuantity) FROM cart WHERE accountID={session['accountID']}")
    cartCount=cursor.fetchone()

    return cartCount

def getCartSum():
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute(f"SELECT SUM(products.`price`) FROM products JOIN cart ON products.`productID`=cart.`productID` WHERE cart.`accountID`={session['accountID']}")
    cartSum=cursor.fetchone()

    helper=""
    for i in cartSum:
        if i is None:
            break
        helper+=str(i)

    if helper == "":
        helper=""
    else:
        helper=int(helper)

    return helper


# checkout functions ----------------------------------------------------------------------------------------------



# misc functions ----------------------------------------------------------------------------------------------
def getProducts():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM products WHERE quantity!=0 AND isArchived=0 LIMIT 10")
    rows = cursor.fetchall()

    return rows

def getProductPictures():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM products WHERE quantity!=0 AND isArchived=0 LIMIT 10")
    rows = cursor.fetchall()
    pictureFiles=[]

    for row in rows:
        pictureFile=row[2].decode(encoding='utf-8')
        pictureFiles.append(pictureFile)

    return pictureFiles

def getStoreName():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    cursor.execute(f"SELECT profiles_seller.`storeName`, profiles_seller.`accountID`, products.`accountID` FROM profiles_seller JOIN products ON profiles_seller.`accountID`=products.`accountID`")
    row = cursor.fetchone()

    if row is None:
        return "none"

    return row

def getLatestProducts():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM products ORDER BY productID DESC LIMIT 10")
    rows = cursor.fetchall()

    return rows

def getLatestProductPictures():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))

    cursor = conn.cursor() 
    cursor.execute(f"SELECT * FROM products ORDER BY productID DESC LIMIT 10")
    rows=cursor.fetchall()
    pictureFiles=[]

    # FIXME: COULDNT SHOW IMAGES
    # FIXED: DONT EVER USE URL_FOR FOR IMAGES, SHIT DOESNT WORK. JUST GO FOR /static/imgs/SHIT
    for row in rows:
        pictureFile=row[2].decode(encoding='utf-8')
        pictureFiles.append(pictureFile)

    return pictureFiles

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
        return 'none'

    return addressBookRow
