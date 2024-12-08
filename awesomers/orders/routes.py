from . import orders
from awesomers.products.routes import getWishlist, getCart, getCartCount, getCartTotalPrice, getCartItemPrice, getCartProductIDs, clearCart, getCartItemQuantity, getCartTotalPrice
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
    cartSum=getCartTotalPrice()
    wishlist=getWishlist()

    cursor=conn.cursor()
    try:
        sql = 'SELECT * FROM order_details WHERE accountID=%s AND orderDetailsID=%s'
        val=session['accountID'], orderDetailsID
        cursor.execute(sql, val)
        orderDetails=cursor.fetchone()

        orderProductDetails=getOrderProductDetails(orderDetailsID)
        orderAddressDetails=getAddressInfoFromOrderDetails(orderDetailsID, orderDetails[3])
        orderStoreDetails=getStoreNameFromOrderDetails(orderDetailsID, orderDetails[2])
        orderProductDetailsPictures=getOrderProductDetailsPictures(orderDetailsID)

        return render_template('products/orders/order_details.html', legend="Order details", wishlistInfo=wishlist, orderAddressInfo=orderAddressDetails, orderStoreInfo=orderStoreDetails, orderProductDetailsInfo=orderProductDetails, orderProductPicturesInfo=orderProductDetailsPictures, orderDetailsInfo=orderDetails, cartSumInfo=cartSum, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
    except Error as e:
        conn.rollback()
        flash(f'{e}', category='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()


# order-buyer functions ----------------------------------------------------------------------------------------------
@orders.route('/place-order', methods=['GET', 'POST'])
def placeOrder():
    dateNow = datetime.now()
    if request.method=='POST':
        accountID = session['accountID']
        storeID = getStoreProfileFromCart()[3]
        buyerAddressID = request.form['buyerAddressOrder']
        paymentMethod = request.form['paymentMethodOrder']
        orderStatus = 'Pending'
        datePlaced = dateNow
        orderTotal=getCartTotalPrice()
    
        conn=get_db_connection()
        if conn is None:
            flash("TANGINA MO WALANG DB BOY", category='error')
            return redirect(url_for('users.login'))

        cursor=conn.cursor()

        try:
            sql = 'INSERT INTO order_details (accountID, sellerProfileID, buyerAddressID, orderStatus, orderTotal, paymentMethod, datePlaced) VALUES (%s, %s, %s, %s, %s, %s, %s)'
            val = accountID, storeID, buyerAddressID, orderStatus, orderTotal, paymentMethod, datePlaced
            cursor.execute(sql, val)
            conn.commit()
            i=0
            while i<len(getCartProductIDs()):
                sql1 = 'INSERT INTO orders (orderDetailsID, accountID, productID, orderQuantity, orderItemSum, orderStatus) VALUES ((SELECT orderDetailsID FROM order_details ORDER BY orderDetailsID DESC LIMIT 1), %s, %s, %s, %s, %s)'
                val1 = accountID, getCartProductIDs()[i], getCartItemQuantity()[i], (getCartItemQuantity()[i]*getCartItemPrice()[i]), orderStatus
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
                sql3 = 'UPDATE products SET quantitySold=quantitySold+%s WHERE productID=%s'
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

@orders.route('/place-order-again/<productID>', methods=['GET', 'POST'])
def buyAgain(productID):
    if request.method=='POST':
        accountID = session['accountID']

        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))

        cursor=conn.cursor()

        # prevent adding out of stock ordered products
        sql2='SELECT quantity FROM products WHERE productID=%s'
        val2=productID
        cursor.execute(sql2, (val2,))
        isProductOutOfStock=cursor.fetchone()
        if isProductOutOfStock[0]==0:
            flash('Product out of stock!', category='error')
            return redirect(url_for('homepage.viewDashboard'))

        # prevents duplicate cart items
        sql1 = "SELECT * FROM cart WHERE productID=%s AND accountID=%s"
        val1 = productID, accountID
        cursor.execute(sql1, val1)
        isProductInCart=cursor.fetchone()
        if isProductInCart:
            sql2="UPDATE cart SET cartQuantity=cartQuantity+%s WHERE productID=%s and accountID=%s"
            val2=1, productID, accountID
            cursor.execute(sql2, val2)
            conn.commit()
            flash("Successfully updated cart product quantity!", category='success')
            return redirect(url_for('homepage.viewDashboard'))

        try:
            sql = "INSERT INTO cart (accountID, productID, cartQuantity) VALUES (%s, %s, %s)"
            val = accountID, productID, 1
            cursor.execute(sql, val)
            conn.commit()
            flash("Successfully added product to cart!", category='success')
            return redirect(url_for('homepage.viewDashboard'))
        except Error as e:
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('homepage.viewDashboard'))
        finally:
            cursor.close()
            conn.close()

@orders.route('/delete-order/<orderDetailsID>', methods=['GET', 'POST'])
def deleteOrder(orderDetailsID):
    if request.method=='POST':
        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECT", category='error')
            return redirect(url_for('users.landing'))
        
        cursor=conn.cursor()

        try:
            sql='DELETE FROM order_details WHERE orderDetailsID=%s and accountID=%s'
            val=orderDetailsID, session['accountID']
            cursor.execute(sql, val)
            conn.commit()
            flash("Successfully deleted order!", category='error')
            return redirect(url_for('homepage.viewDashboard'))
        except Error as e:
            conn.rollback()
            flash(f'{e}', category='error')
            return redirect(url_for('homepage.viewDashboard'))
        finally:
            cursor.close()
            conn.close()


# order-seller functions ----------------------------------------------------------------------------------------------
@orders.route('/seller/cancel-order/<productID>/<quantity>/<orderID>', methods=['GET', 'POST'])
def cancelOrder(productID, quantity, orderID):
    if request.method=='POST':
        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECT", category='error')
            return redirect(url_for('users.landing'))
        
        cursor=conn.cursor()

        try:
            sql='UPDATE orders SET orderStatus=%s WHERE productID=%s AND orderID=%s'
            val='Cancelled', productID, orderID
            cursor.execute(sql, val)
            conn.commit()
            sql1='UPDATE products SET quantity=quantity+%s WHERE productID=%s'
            val1=quantity, productID
            cursor.execute(sql1, val1)
            conn.commit()
            sql2='UPDATE products SET quantitySold=quantitySold-%s WHERE productID=%s'
            val2=quantity, productID
            cursor.execute(sql2, val2)
            conn.commit()
            flash("Successfully cancelled order!", category='success')
            return redirect(url_for('seller.renderOrders'))
        except Error as e:
            conn.rollback()
            flash(f'{e}', category='error')
            return redirect(url_for('seller.renderOrders'))
        finally:
            cursor.close()
            conn.close()

@orders.route('/seller/update-orderdetails-status/<orderDetailsID>', methods=['GET', 'POST'])
def updateOrderDetailsStatus(orderDetailsID):
    if request.method=='POST':
        orderStatus=request.form.get('orderDetailsStatus')

        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECT", category='error')
            return redirect(url_for('users.landing'))
        
        cursor=conn.cursor()

        try:
            sql='UPDATE order_details SET orderStatus=%s WHERE orderDetailsID=%s'
            val=orderStatus, orderDetailsID
            cursor.execute(sql, val)
            conn.commit()
            sql='UPDATE orders SET orderStatus=%s WHERE orderDetailsID=%s AND orderStatus!="Cancelled"'
            val=orderStatus, orderDetailsID
            cursor.execute(sql, val)
            conn.commit()
            flash("Successfully updated order status!", category='success')
            return redirect(url_for('seller.renderOrders'))
        except Error as e:
            conn.rollback()
            flash(f'{e}', category='error')
            return redirect(url_for('seller.renderOrders'))
        finally:
            cursor.close()
            conn.close()

@orders.route('/seller/update-status/<productID>/<orderID>', methods=['GET', 'POST'])
def updateOrderStatus(productID, orderID):
    if request.method=='POST':
        orderStatus=request.form.get('orderStatus')

        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECT", category='error')
            return redirect(url_for('users.landing'))
        
        cursor=conn.cursor()

        try:
            sql='UPDATE orders SET orderStatus=%s WHERE productID=%s AND orderID=%s AND orderStatus!="Cancelled"'
            val=orderStatus, productID, orderID
            cursor.execute(sql, val)
            conn.commit()
            flash("Successfully updated order status!", category='success')
            return redirect(url_for('seller.renderOrders'))
        except Error as e:
            conn.rollback()
            flash(f'{e}', category='error')
            return redirect(url_for('seller.renderOrders'))
        finally:
            cursor.close()
            conn.close()


# order getter functions ----------------------------------------------------------------------------------------------
def getOrderDetails():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECT", category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()

    sql = 'SELECT * FROM order_details WHERE accountID=%s'
    val=session['accountID']
    cursor.execute(sql, (val,))
    details=cursor.fetchall()

    return details 

def getOrderProductDetails(orderDetailsID):
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    sql = 'SELECT orders.`orderDetailsID`, orders.`orderID`, products.`picture`, products.`productName`, products.`price`, orders.`orderQuantity`, products.`productID`, orders.`orderItemSum`, orders.`orderStatus` FROM products JOIN orders ON products.`productID`=orders.`productID` WHERE orders.`accountID`=%s AND orders.`orderDetailsID`=%s ORDER BY orders.`orderDetailsID` DESC'
    val = session['accountID'], orderDetailsID
    cursor.execute(sql, val)
    orders=cursor.fetchall()

    return orders

def getOrderProductDetailsPictures(orderDetailsID):
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    sql='SELECT * FROM products JOIN orders ON products.`productID`=orders.`productID` WHERE orders.`accountID`=%s AND orders.`orderDetailsID`=%s ORDER BY orders.`orderDetailsID` DESC'
    val = session['accountID'], orderDetailsID
    cursor.execute(sql, val)
    orders=cursor.fetchall()
    pictureFiles=[]

    for order in orders:
        pictureFile=order[2].decode(encoding='utf-8')
        pictureFiles.append(pictureFile)

    return pictureFiles

def getOrderProductIDs():
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE accountID=%s', (session['accountID'], ))
    orders=cursor.fetchall()

    return orders


# misc getter functions ----------------------------------------------------------------------------------------------
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

def getOrderDetailsIDs(sellerProfileID):
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    cursor.execute('SELECT orderDetailsID FROM order_details WHERE sellerProfileID=%s', (sellerProfileID, ))
    orders=cursor.fetchall()
    results = [o[0] for o in orders]

    return results

def getOrderProductItems():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECT", category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()

    sql = 'SELECT orders.`orderDetailsID`, orders.`orderID`, products.`picture`, products.`productName`, products.`price`, orders.`orderQuantity`, products.`productID`, orders.`orderStatus` FROM products JOIN orders ON products.`productID`=orders.`productID` WHERE orders.`accountID`=%s ORDER BY orders.`orderDetailsID` DESC'
    val=session['accountID']
    cursor.execute(sql, (val,))
    details=cursor.fetchall()

    return details 

def getAddressInfoFromOrderDetails(orderDetailsID, buyerAddressID):
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECT", category='error')
        return redirect(url_for('users.landing'))

    cursor=conn.cursor()
    sql='SELECT * FROM address_book JOIN order_details ON address_book.`accountID`=order_details.`accountID` WHERE order_details.`buyerAddressID`=%s AND order_details.`accountID`=%s AND order_details.`orderDetailsID`=%s'
    val=buyerAddressID, session['accountID'], orderDetailsID
    cursor.execute(sql, val)
    addressRow = cursor.fetchone()

    return addressRow

def getStoreNameFromOrderDetails(orderDetailsID, sellerProfileID):
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECT", category='error')
        return redirect(url_for('users.landing'))

    cursor=conn.cursor()
    sql='SELECT * FROM profiles_seller JOIN order_details ON profiles_seller.`sellerProfileID`=order_details.`sellerProfileID` WHERE order_details.`orderDetailsID`=%s AND order_details.`accountID`=%s AND order_details.`sellerProfileID`=%s'
    val=orderDetailsID, session['accountID'], sellerProfileID
    cursor.execute(sql, val)
    storeNameRow = cursor.fetchone()

    return storeNameRow


# order-seller getter functions ----------------------------------------------------------------------------------------------
def getOrderDetailsForSeller(sellerProfileID):
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECT", category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    sql = 'SELECT * FROM order_details WHERE sellerProfileID=%s'
    val = sellerProfileID
    cursor.execute(sql, (val, ))
    details = cursor.fetchall()

    return details

def getOrderProductDetailsForSeller(orderDetailsID):
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECT", category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    sql='SELECT orders.`orderDetailsID`, orders.`orderID`, products.`picture`, products.`productName`, products.`price`, orders.`orderQuantity`, products.`productID`, orders.`orderItemSum`, orders.`orderStatus` FROM products JOIN orders ON products.`productID`=orders.`productID` WHERE orders.`orderDetailsID`=%s'
    val = orderDetailsID
    cursor.execute(sql, (val,))
    details = cursor.fetchall()

    return details

def getBuyerNameForSellerOrders(sellerProfileID):
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    sql='SELECT * FROM profiles_buyer JOIN order_details ON order_details.`accountID`=profiles_buyer.`accountID` WHERE order_details.`sellerProfileID`=%s'
    val=sellerProfileID
    cursor.execute(sql, (val,))
    details=cursor.fetchall()

    return details

def getBuyerAddressForSellerOrders(sellerProfileID):
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    sql='SELECT * FROM address_book JOIN order_details ON order_details.`accountID`=address_book.`accountID` WHERE order_details.`sellerProfileID`=%s'
    val=sellerProfileID
    cursor.execute(sql, (val,))
    details=cursor.fetchall()

    return details

def getBuyerAddressForSellerOrderDetails(sellerProfileID, orderDetailsID):
    conn = get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('homepage.home'))
    
    cursor = conn.cursor()
    sql='SELECT * FROM address_book JOIN order_details ON order_details.`accountID`=address_book.`accountID` JOIN orders ON orders.`orderDetailsID`=order_details.`orderDetailsID` WHERE order_details.`sellerProfileID`=%s AND orders.`orderDetailsID`=%s'
    val=sellerProfileID, orderDetailsID
    cursor.execute(sql, val)
    details=cursor.fetchall()

    return details

def getSellerOrderCount(sellerProfileID):
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECT", category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    sql = 'SELECT * FROM order_details WHERE sellerProfileID=%s'
    val = sellerProfileID
    cursor.execute(sql, (val, ))
    details = cursor.fetchall()

    return details

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