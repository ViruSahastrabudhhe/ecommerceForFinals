from . import orders
from awesomers.products.routes import getCart, getCartCount, getCartProductIDs
from flask import render_template, redirect, url_for, flash, session, request
from awesomers.users.routes import logout
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection
from datetime import datetime, date
import uuid as uuid

@orders.route('/place-order', methods=['GET', 'POST'])
def placeOrder():
    dateNow = datetime.now()
    if request.method=='POST':
        accountID = session['accountID']
        buyerAddressID = request.form['buyerAddressOrder']
        paymentMethod = request.form['paymentMethodOrder']
        orderStatus = 'To Ship'
        datePlaced = dateNow
    
        conn=get_db_connection()
        if conn is None:
            flash("TANGINA MO WALANG DB BOY", category='error')
            return redirect(url_for('users.login'))

        cursor=conn.cursor()

        try:
            sql = 'INSERT INTO order_details (accountID, buyerAddressID, orderStatus, paymentMethod, datePlaced) VALUES (%s, %s, %s, %s, %s)'
            val = accountID, buyerAddressID, orderStatus, paymentMethod, datePlaced
            cursor.execute(sql, val)
            conn.commit()
            i=0
            while i<len(getCartProductIDs()):
                sql1 = 'INSERT INTO orders (orderDetailsID, accountID, productID) VALUES ((SELECT orderDetailsID FROM order_details ORDER BY orderDetailsID DESC LIMIT 1), %s, %s)'
                val1 = accountID, getCartProductIDs()[i]
                cursor.execute(sql1, val1)
                conn.commit()
                i+=1
            flash('Order placed!', category='success')
            return redirect(url_for('products.viewCheckout'))
        except Error as e:
            conn.rollback()
            flash(f'{e}', category='error')
            return redirect(url_for('products.viewCheckout'))
        finally:
            cursor.close()
            conn.close()

def getOrderDetails():
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM order_details WHERE accountID=%s', (session['accountID'], ))
    orders=cursor.fetchall()
    return orders

def getOrderProductIDs():
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE accountID=%s', (session['accountID'], ))
    orders=cursor.fetchall()
    return orders

def getOrderProductDetails():
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM products JOIN orders ON products.`productID`=orders.`productID` WHERE orders.`accountID`=%s', (session['accountID'], ))
    orders=cursor.fetchall()
    return orders


# INSERT INTO orders_details (accountID, storeAddressID, buyerAddressID, orderStatus) VALUES (42, 1, 1, 1);
# INSERT INTO orders (orderID, accountID, productID) VALUES (LAST_INSERT_ID(), 1, 1);
# SELECT * FROM orders

# sql1 = 'INSERT INTO orders (orderID, accountID, productID) VALUES ((SELECT orderDetailsID FROM order_details ORDER BY orderDetailsID DESC LIMIT 1), %s, %s)'
# val1 = accountID, id[0]
# cursor.execute(sql1, val1)
# conn.commit()
# print("ORDERS LOL")

# INSERT INTO order_details (accountID, buyerAddressID, orderStatus, paymentMethod) VALUES (42, 82, 1,1);
# INSERT INTO orders (orderDetailsID, accountID, productID) VALUES ((SELECT orderDetailsID FROM order_details ORDER BY orderDetailsID DESC LIMIT 1), 42, 32);
# SELECT * FROM orders