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
    cartRows=viewCart()
    cartCount = getCartCount()

    try:
        cursor.execute(f'SELECT * FROM products WHERE productID={productID}')
        row=cursor.fetchone()
        pictureFile = row[2].decode(encoding='utf-8')
        return render_template('products/product_info.html', legend="Product information", productIDInfo=row, productIDPicture=pictureFile, productInfo=productRows, productPictureInfo=productRowPictures, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        flash(f"{e}", cateogry='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()

@products.route('/cart/view-cart')
def viewCart():
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute(f"SELECT products.`productName`, products.`quantity`, products.`price`, cart.`productID` FROM products JOIN cart ON products.`productID` = cart.`productID` WHERE cart.`accountID`={session['accountID']}")
    cartRows=cursor.fetchall()

    return cartRows


# cart functions ----------------------------------------------------------------------------------------------
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
    cursor.execute(f"SELECT COUNT(*) FROM cart WHERE accountID={session['accountID']}")
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
        helper+=str(i)
    helper=int(helper)

    return helper


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