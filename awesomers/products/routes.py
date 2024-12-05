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
        conn.rollback()
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
    cartSum =getCartPriceSum()
    storeName=getStoreName()
    addressBookRows=getAddressBookRows()

    if getAddressBookRows()=='none':
        return render_template('products/checkout.html', productInfo=productRows, productPictureInfo=productRowPictures, storeNameInfo=storeName, addressBookInfo=addressBookRows, cartInfo=cartRows, cartPicturesInfo=cartPicturesRows, cartCountInfo = cartCount, cartSumInfo=cartSum, isAddress='false', legend="Checkout", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    return render_template('products/checkout.html', productInfo=productRows, productPictureInfo=productRowPictures, storeNameInfo=storeName, addressBookInfo=addressBookRows, cartInfo=cartRows, cartPicturesInfo=cartPicturesRows, cartCountInfo = cartCount, cartSumInfo=cartSum, isAddress='true', legend="Checkout", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])


# cart functions ----------------------------------------------------------------------------------------------
def getCart():
    accountID=session['accountID']
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    sql = 'SELECT products.`productName`, cart.`cartQuantity`, products.`price`, cart.`productID`, products.`quantity` FROM products JOIN cart ON products.`productID` = cart.`productID` WHERE cart.`accountID`=%s'
    cursor.execute(sql, (accountID,))
    cartRows=cursor.fetchall()

    return cartRows

def getCartPictures():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))

    cursor = conn.cursor() 
    cursor.execute('SELECT * FROM products JOIN cart ON products.`productID` = cart.`productID` WHERE cart.`accountID`=%s', (session['accountID'], ))
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
        cartQuantity = request.form.get('cartQuantity')

        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))

        cursor=conn.cursor()
        
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
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('homepage.home'))
        finally:
            cursor.close()
            conn.close()

@products.route('/cart/update-cart-item/<productID>', methods=['GET', 'POST'])
def updateCart(productID):
    if request.method=='POST':
        accountID = session['accountID']
        cartQuantity = request.form.get('cartQuantity')

        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))
        
        cursor=conn.cursor()

        if cartQuantity==0:
            cursor.execute('DELETE FROM cart WHERE accountID=%s AND productID=%s', (accountID, productID))
            flash(f"Successfully deleted item in cart!", category='error')
            return redirect(url_for('homepage.home'))

        # sql = "SELECT cart.`cartQuantity`, products.`productName`, products.`quantity` FROM products JOIN cart ON products.`productID`=cart.`productID` WHERE cart.`accountID`=%s AND cart.`productID`=%s AND cart.`cartQuantity`+%s <= (SELECT quantity FROM products WHERE productID=%s)"
        # # FIXME: db cart has 4, then cartQuantity = 19 ANG NANGYAYARI AY NAIINCREMENT UNG INITIAL VALUE WITH THE NUMBER WE INPUTTED
        # val = accountID, productID, cartQuantity, productID
        # cursor.execute(sql, val)
        # isRowInCart = cursor.fetchone()
            
        # if isRowInCart is None:
        #     flash(f"Not enough stock left in store!", category='error')
        #     return redirect(url_for('homepage.home'))
        
        try:
            sql = "UPDATE cart SET cartQuantity=%s WHERE productID=%s AND accountID=%s"
            val = cartQuantity,productID, accountID
            cursor.execute(sql, val)
            conn.commit()
            flash(f"Successfully updated quantity!", category='success')
            return redirect(url_for('homepage.home'))
        except Error as e:
            conn.rollback()
            flash(f'{e}', category='error')
            return redirect(url_for('homepage.home'))
        finally:
            cursor.close()
            conn.close()
    # SELECT * FROM products JOIN cart ON products.`productID`=cart.`productID` WHERE cart.`accountID`=42 AND cart.`productID`=42 AND cart.`cartQuantity`+22= (SELECT quantity FROM products WHERE productId=42)
    # print("CHECK THIS OUT GUS")
    # print(cartQuantity)
    # if cartQuantity==0:
    # print("CHECK THIS OUT GUS")
    # cursor.execute('DELETE FROM cart WHERE productID=%s and accountID=%s', (productID, accountID))
    # conn.commit()
    # flash(f"Successfully deleted product from cart! {cartQuantity}, {productID}, {accountID}", category='success')

@products.route('/cart/delete-cart-item/<productID>', methods=['GET', 'POST'])
def deleteCart(productID):
    if request.method=='POST':
        accountID=session['accountID']

        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))

        cursor=conn.cursor()

        try:
            cursor.execute('DELETE FROM cart WHERE productID=%s and accountID=%s', (productID, accountID))
            conn.commit()
            flash('Successfully deleted cart item!', category='error')
            return redirect(url_for('homepage.home'))
        except Error as e:
            conn.rollback()
            flash(f'{e}', category='error')
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

    try:
        cursor.execute("DELETE FROM cart WHERE accountID=%s", (session['accountID'], ))
        conn.commit()
        flash("Cart contents cleared!", category='success')
        return redirect(url_for('homepage.home'))
    except Error as e:
        conn.rollback()
        flash(f"{e}", category='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()

def getCartCount():
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute("SELECT SUM(cartQuantity) FROM cart WHERE accountID=%s", (session['accountID'], ))
    cartCount=cursor.fetchone()

    return cartCount

def getCartPriceSum():
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute("SELECT SUM(products.`price`*cart.`cartQuantity`) FROM products JOIN cart ON products.`productID`=cart.`productID` WHERE cart.`accountID`=%s", (session['accountID'], ))
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

def getCartProductIDs():
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    sql = 'SELECT productID FROM cart WHERE accountID=%s'
    val = session['accountID']
    cursor.execute(sql, (val,))
    rows=cursor.fetchall()
    results = [i[0] for i in rows]

    return results

def getCartItemQuantity():
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    sql = 'SELECT cartQuantity FROM cart WHERE accountID=%s'
    val = session['accountID']
    cursor.execute(sql, (val,))
    rows=cursor.fetchall()
    results = [i[0] for i in rows]

    return results


# misc functions ----------------------------------------------------------------------------------------------
def getProducts():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    try:
        cursor.execute("SELECT * FROM products WHERE quantity!=0 AND isArchived=0 LIMIT 10")
        rows = cursor.fetchall()
    except:
        conn.rollback()

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
    cursor.execute("SELECT profiles_seller.`storeName`, profiles_seller.`accountID`, products.`accountID` FROM profiles_seller JOIN products ON profiles_seller.`accountID`=products.`accountID`")
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
    cursor.execute("SELECT * FROM products ORDER BY productID DESC LIMIT 10")
    rows = cursor.fetchall()

    return rows

def getLatestProductPictures():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))

    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM products ORDER BY productID DESC LIMIT 10")
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
    cursor.execute("SELECT * FROM profiles_buyer WHERE accountID=%s", (session['accountID'], ))
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