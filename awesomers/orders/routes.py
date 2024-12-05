from . import orders
from awesomers.products.routes import getCart, getCartCount, getCartPriceSum, getCartProductIDs, clearCart, getCartItemQuantity
from flask import render_template, redirect, url_for, flash, session, request
from awesomers.users.routes import logout
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection
from datetime import datetime, date

# renders ----------------------------------------------------------------------------------------------
@orders.route('/orders/view-order/<orderDetailsID>')
def viewOrderDetails(orderDetailsID):
    if session['loggedIn'] == False:
        flash('Please log in first!', category='error')
        return redirect(url_for('users.landing'))
    
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))

    cartRows=getCart()
    cartCount = getCartCount()
    cartSum=getCartPriceSum()

    cursor=conn.cursor()
    try:
        sql = 'SELECT * FROM order_details WHERE accountID=%s AND orderDetailsID=%s'
        val=session['accountID'], orderDetailsID
        cursor.execute(sql, val)
        orderDetails=cursor.fetchall()
        orderProductDetails=getOrderProductDetails()
        return render_template('products/orders/order_details.html', legend="Order details", orderProductDetailsInfo=orderProductDetails, orderDetailsInfo=orderDetails, cartSumInfo=cartSum, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        conn.rollback()
        flash(f'{e}', category='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()


# order functions ----------------------------------------------------------------------------------------------
@orders.route('/place-order', methods=['GET', 'POST'])
def placeOrder():
    dateNow = datetime.now()
    if request.method=='POST':
        accountID = session['accountID']
        storeID = getStoreProfileFromCart()[3]
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
            sql = 'INSERT INTO order_details (accountID, sellerProfileID, buyerAddressID, orderStatus, paymentMethod, datePlaced) VALUES (%s, %s, %s, %s, %s, %s)'
            val = accountID, storeID, buyerAddressID, orderStatus, paymentMethod, datePlaced
            cursor.execute(sql, val)
            conn.commit()
            i=0
            while i<len(getCartProductIDs()):
                sql1 = 'INSERT INTO orders (orderDetailsID, accountID, productID, orderQuantity) VALUES ((SELECT orderDetailsID FROM order_details ORDER BY orderDetailsID DESC LIMIT 1), %s, %s, %s)'
                val1 = accountID, getCartProductIDs()[i], getCartItemQuantity()[i]
                cursor.execute(sql1, val1)
                conn.commit()
                i+=1
            i=0
            while i<len(getCartProductIDs()):
                sql2 = 'UPDATE products SET quantity=quantity-%s WHERE productID=%s'
                val2 = getCartItemQuantity()[i], getCartProductIDs()[i]
                cursor.execute(sql2, val2)
                conn.commit()
                i+=1
            i=0
            while i<len(getCartProductIDs()):
                sql3 = 'UPDATE products SET quantitySold=%s WHERE productID=%s'
                val3 = getCartItemQuantity()[i], getCartProductIDs()[i]
                cursor.execute(sql3, val3)
                conn.commit()
                i+=1
            clearCart()
            flash('Order placed!', category='success')
            return redirect(url_for('homepage.viewDashboard'))
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

def getOrderProductDetails():
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    sql = 'SELECT orders.`orderDetailsID`, orders.`orderID`, products.`picture`, products.`productName`, products.`price`, orders.`orderQuantity`, products.`productID` FROM products JOIN orders ON products.`productID`=orders.`productID` WHERE orders.`accountID`=%s ORDER BY orders.`orderDetailsID` DESC'
    val = session['accountID']
    cursor.execute(sql, (val, ))
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


# misc functions ----------------------------------------------------------------------------------------------
def getStoreProfileFromCart():
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    sql='SELECT products.`productName`, products.`productID`, products.`accountID`, profiles_seller.`sellerProfileID` FROM products JOIN profiles_seller ON products.`accountID`=profiles_seller.`accountID` JOIN cart ON products.`productID`=cart.`productID` WHERE products.`productID`=cart.`productID` AND cart.`accountID`=%s GROUP BY profiles_seller.`sellerProfileID`'
    val=session['accountID']
    cursor.execute(sql, (val,))
    profileRow = cursor.fetchone()

    return profileRow

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

# SELECT products.`accountID`, profiles_seller.`sellerProfileID` FROM products JOIN orders ON products.`productID`=orders.`productID` JOIN profiles_seller ON products.`accountID`=profiles_seller.`accountID`
# SELECT cart.`productID` AS product_cartID, profiles_seller.`accountID` AS store_profileID, products.`accountID` AS product_storeID FROM products JOIN cart ON products.`productID`=cart.`productID` JOIN profiles_seller ON products.`accountID`=profiles_seller.`accountID`
# SELECT products.`productName`, products.`productID`, products.`accountID`, profiles_seller.`sellerProfileID` FROM products JOIN profiles_seller ON products.`accountID`=profiles_seller.`accountID` JOIN cart ON products.`productID`=cart.`productID` WHERE products.`productID`=cart.`productID` AND cart.`accountID`=42
# SELECT products.`productName`, products.`productID`, products.`accountID`, profiles_seller.`sellerProfileID` FROM products JOIN profiles_seller ON products.`accountID`=profiles_seller.`accountID` JOIN orders ON products.`productID`=orders.`productID` WHERE products.`productID`=orders.`productID` AND orders.`accountID`=42
# SELECT * FROM products JOIN orders ON products.`productID`=orders.`productID` JOIN order_details ON products.`accountID`=order_details.`accountID` WHERE orders.`accountID`=42 AND orders.`orderDetailsID`=(SELECT orderDetailsID FROM order_details WHERE accountID=42 ORDER BY orderDetailsID DESC LIMIT 1)
# SELECT products.`productName`, products.`price`, products.`quantity`, orders.`orderDetailsID` FROM products JOIN orders ON products.`productID`=orders.`productID` WHERE orders.`accountID`=42
# SELECT orders.`productID`, order_details.`orderDetailsID` FROM order_details JOIN orders ON orders.`orderDetailsID`=order_details.`orderDetailsID` WHERE order_details.`accountID`=42 AND orders.`orderDetailsID`=5