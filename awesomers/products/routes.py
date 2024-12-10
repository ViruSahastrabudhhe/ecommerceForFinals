from . import products
from flask import render_template, redirect, url_for, flash, session, request
from awesomers.users.routes import logout
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection
from datetime import datetime
import uuid as uuid
import pathlib
import os
from datetime import datetime

# renders ----------------------------------------------------------------------------------------------
@products.route('/home/product-info/<productID>')
def viewProductPage(productID):
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    productRows=getAvailableProducts()
    productRowPictures=getAvailableProductPictures()
    cartRows=getCart()
    cartCount = getCartCount()
    cartSum=getCartTotalPrice()
    storeName=getStoreName()
    wishlist=getWishlist()

    try:
        cursor.execute('SELECT * FROM products WHERE productID=%s', (productID, ))
        row=cursor.fetchone()
        pictureFile = row[2].decode(encoding='utf-8')
        return render_template('products/product_info.html', legend="Product information", wishlistInfo=wishlist, productIDInfo=row, productIDPicture=pictureFile, productInfo=productRows, productPictureInfo=productRowPictures, storeNameInfo=storeName, cartSumInfo=cartSum, cartInfo=cartRows, cartCountInfo = cartCount, id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])
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
    
    productRows=getAvailableProducts()
    productRowPictures=getAvailableProductPictures()
    cartRows=getCart()
    cartPicturesRows=getCartPictures()
    cartCount = getCartCount()
    cartSum =getCartTotalPrice()
    storeName=getStoreName()
    wishlist=getWishlist()
    addressBookRows=getAddressBookRows()

    return render_template('products/checkout.html', wishlistInfo=wishlist, productInfo=productRows, productPictureInfo=productRowPictures, storeNameInfo=storeName, addressBookInfo=addressBookRows, cartInfo=cartRows, cartPicturesInfo=cartPicturesRows, cartCountInfo = cartCount, cartSumInfo=cartSum, isAddress='true', legend="Checkout", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@products.route('/search', methods=['GET'])
def viewSearch():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('users.landing'))
    
    query=request.args.get('searchQuery')
    cursor=conn.cursor()
    sql='SELECT * FROM products WHERE productName LIKE %s'
    val=[query+'%']
    cursor.execute(sql, val) 
    rows=cursor.fetchall()  
    pictureFiles=[]

    for row in rows:
        pictureFile=row[2].decode(encoding='utf-8')
        pictureFiles.append(pictureFile)

    cartRows=getCart()
    cartPicturesRows=getCartPictures()
    cartCount = getCartCount()
    cartSum =getCartTotalPrice()
    wishlist=getWishlist()

    return render_template('products/product_search.html', searchInfo=query, productInfo=rows, productPictureInfo=pictureFiles, wishlistInfo=wishlist, cartInfo=cartRows, cartPicturesInfo=cartPicturesRows, cartCountInfo = cartCount, cartSumInfo=cartSum, isAddress='true', legend="Search products", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@products.route('/search/filtered/<searchQuery>', methods=['GET', 'POST'])
def viewFilteredSearch(searchQuery):
    priceFilter=request.args.get('priceFilter')
    dateFilter=request.args.get('dateFilter')
    cartRows=getCart()
    cartPicturesRows=getCartPictures()
    cartCount = getCartCount()
    cartSum =getCartTotalPrice()
    wishlist=getWishlist()
    availableProducts=getAvailableProducts()
    availableProductsPictures=getAvailableProductPictures()

    return render_template('products/product_search.html', priceFilterInfo=priceFilter, dateFilterInfo=dateFilter, searchInfo=searchQuery, productInfo=availableProducts, productPictureInfo=availableProductsPictures, wishlistInfo=wishlist, cartInfo=cartRows, cartPicturesInfo=cartPicturesRows, cartCountInfo = cartCount, cartSumInfo=cartSum, isAddress='true', legend="Search products", id=session['accountID'], email=session['accountEmail'], fname=session['accountFirstName'], lname=session['accountLastName'], role=session['accountRole'])

@products.route('/landing/search', methods=['GET'])
def viewLandingSearch():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('users.landing'))
    
    query=request.args.get('searchQuery')
    cursor=conn.cursor()
    sql='SELECT * FROM products WHERE productName LIKE %s'
    val=[query+'%']
    cursor.execute(sql, val) 
    rows=cursor.fetchall()  
    pictureFiles=[]

    for row in rows:
        pictureFile=row[2].decode(encoding='utf-8')
        pictureFiles.append(pictureFile)

    cartRows=getCart()
    cartPicturesRows=getCartPictures()
    cartCount = getCartCount()
    cartSum =getCartTotalPrice()
    wishlist=getWishlist()

    return render_template('products/landing_product_search.html', searchInfo=query, productInfo=rows, productPictureInfo=pictureFiles, wishlistInfo=wishlist, cartInfo=cartRows, cartPicturesInfo=cartPicturesRows, cartCountInfo = cartCount, cartSumInfo=cartSum, isAddress='true', legend="Search products", id=session['accountID'], role=session['accountRole'])



# cart functions ----------------------------------------------------------------------------------------------
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

        # prevents duplicate cart items
        sql1 = "SELECT * FROM cart WHERE productID=%s AND accountID=%s"
        val1 = productID, accountID
        cursor.execute(sql1, val1)
        isProductInCart=cursor.fetchone()
        if isProductInCart:
            sql2="UPDATE cart SET cartQuantity=cartQuantity+%s WHERE productID=%s and accountID=%s"
            val2=cartQuantity, productID, accountID
            cursor.execute(sql2, val2)
            conn.commit()
            flash("Successfully updated cart product quantity!", category='success')
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
def deleteCartInCheckout(productID):
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
            return redirect(url_for('products.viewCheckout'))
        except Error as e:
            conn.rollback()
            flash(f'{e}', category='error')
            return redirect(url_for('products.viewCheckout'))
        finally:
            cursor.close()
            conn.close()


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


# cart getter functions ----------------------------------------------------------------------------------------------
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

def getCartCount():
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    cursor.execute("SELECT SUM(cartQuantity) FROM cart WHERE accountID=%s", (session['accountID'], ))
    cartCount=cursor.fetchone()

    return cartCount

def getCartItemPrice():
    conn =get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()
    sql = 'SELECT products.`price` FROM products JOIN cart ON products.`productID`=cart.`productID` WHERE cart.`accountID`=%s'
    val = session['accountID']
    cursor.execute(sql, (val,))
    rows=cursor.fetchall()
    results = [i[0] for i in rows]

    return results

def getCartTotalPrice():
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


# wishlist functions ----------------------------------------------------------------------------------------------
@products.route('/wishlist/add-to-wishlist/<productID>', methods=['GET', 'POST'])
def addToWishlist(productID):
    if request.method=='POST':
        accountID = session['accountID']

        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))

        cursor=conn.cursor()
        sql1='SELECT * FROM wishlist WHERE productID=%s AND accountID=%s'
        val1=productID, accountID
        cursor.execute(sql1, val1)
        isProductInWishlist=cursor.fetchone()
        if isProductInWishlist:
            flash('Product already in wishlist!', category='error')
            return redirect(url_for('products.viewProductPage', productID=productID))

        try:
            sql = 'INSERT INTO wishlist (accountID, productID) VALUES (%s, %s)'
            val = accountID, productID
            cursor.execute(sql, val)
            conn.commit()
            flash('Successfully added to wishlist!', category='success')
            return redirect(url_for('products.viewProductPage', productID=productID))
        except Error as e:
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('products.viewProductPage', productID=productID))
        finally:
            cursor.close()
            conn.close()

@products.route('/wishlist/clear-wishlist', methods=['GET', 'POST'])
def clearWishlist():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()

    try:
        cursor.execute("DELETE FROM wishlist WHERE accountID=%s", (session['accountID'], ))
        conn.commit()
        flash("Wishlist contents cleared!", category='success')
        return redirect(url_for('homepage.home'))
    except Error as e:
        conn.rollback()
        flash(f"{e}", category='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()

@products.route('/wishlist/delete-wishlist-item/<productID>', methods=['GET', 'POST'])
def deleteWishlist(productID):
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))
    
    cursor=conn.cursor()

    try:
        cursor.execute("DELETE FROM wishlist WHERE accountID=%s AND productID=%s", (session['accountID'], productID))
        conn.commit()
        flash("Successfully deleted wishlist item!", category='success')
        return redirect(url_for('homepage.home'))
    except Error as e:
        conn.rollback()
        flash(f"{e}", category='error')
        return redirect(url_for('homepage.home'))
    finally:
        cursor.close()
        conn.close()

@products.route('/wishlist/add-wishlist-item-to-cart/<productID>', methods=['GET', 'POST'])
def addWishlistToCart(productID):
    if request.method=='POST':
        accountID = session['accountID']

        conn=get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))

        cursor=conn.cursor()

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
            deleteWishlist(productID)
            flash("Successfully updated cart product quantity!", category='success')
            return redirect(url_for('homepage.home'))

        try:
            sql = "INSERT INTO cart (accountID, productID, cartQuantity) VALUES (%s, %s, %s)"
            val = accountID, productID, 1
            cursor.execute(sql, val)
            conn.commit()
            deleteWishlist(productID)
            flash("Successfully added product to cart!", category='success')
            return redirect(url_for('homepage.home'))
        except Error as e:
            conn.rollback()
            flash(f"{e}", category='error')
            return redirect(url_for('homepage.home'))
        finally:
            cursor.close()
            conn.close()

def getWishlist():
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    sql='SELECT products.`productID`, products.`productName`, products.`quantity`, products.`price` FROM products JOIN wishlist ON products.`productID`=wishlist.`productID` WHERE wishlist.`accountID`=%s'
    val=session['accountID']
    cursor.execute(sql, (val,))
    wishlist=cursor.fetchall()

    return wishlist



# misc getter functions ----------------------------------------------------------------------------------------------
def getAvailableProducts():
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

def getAvailableProductPictures():
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

    return addressBookRow

def getBestSellingProducts():
    conn=get_db_connection()
    if conn is None:
        flash('NO DB CONNECTION', category='error')
        return redirect(url_for('users.landing'))
    
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY quantitySold DESC LIMIT 10')
    products=cursor.fetchall()

    return products

def getBestSellingProductsPictures():
    conn=get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('homepage.home'))

    cursor = conn.cursor() 
    cursor.execute('SELECT * FROM products ORDER BY quantitySold DESC LIMIT 10')
    rows=cursor.fetchall()
    pictureFiles=[]

    # FIXME: COULDNT SHOW IMAGES
    # FIXED: DONT EVER USE URL_FOR FOR IMAGES, SHIT DOESNT WORK. JUST GO FOR /static/imgs/SHIT
    for row in rows:
        pictureFile=row[2].decode(encoding='utf-8')
        pictureFiles.append(pictureFile)

    return pictureFiles