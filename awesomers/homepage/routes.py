from . import homepage
from flask import render_template, redirect, url_for, flash, session, request
from awesomers.users.routes import logout
import mysql.connector
from mysql.connector import Error
from awesomers.models import get_db_connection

@homepage.route('/home')
def home():
    if session['accountRole']=='seller':
        return render_template('dashboard/dashboard_seller.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])
    elif session['accountRole']=='buyer':
        return render_template('dashboard/dashboard_buyer.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

# buyer ----------------------------------------------------------------------------------------------
@homepage.route('/renderBuyerBecomeSeller')
def renderBuyerBecomeSeller():
    return render_template('dashboard/dashboard_buyer.html', purpose="renderBuyerBecomeSeller", id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])

@homepage.route('/requestToBecomeSeller', methods=['GET', 'POST'])
def requestToBecomeSeller():
    if request.method=="POST":
        id = session['accountID']
        email = session['accountEmail']
        requestType = "BUYER TO BE SELLER"

        conn = get_db_connection()
        if conn is None:
            flash("NO DB CONNECTION", category='error')
            return redirect(url_for('homepage.home'))   
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO requests (accountID, accountEmail, requestType, requestArchived) VALUES (%s, %s, %s, %s)', (id, email, requestType, 0))
            conn.commit()
            flash("CREATED NEW REQUEST", category="success")
        except mysql.connector.IntegrityError:  
            conn.rollback()
            flash("REQUEST ALREADY EXISTO", category='error')
            return redirect(url_for('homepage.renderBuyerBecomeSeller'))
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('homepage.home'))
    
    return render_template('dashboard/dashboard_buyer.html', id=session['accountID'], email=session['accountEmail'], username=session['accountUsername'], role=session['accountRole'])


# seller ----------------------------------------------------------------------------------------------
@homepage.route("/redirectToSellerCenter",)
def redirectToSellerCenter():
    return redirect(url_for('seller.sellerCenter'))

# admin ----------------------------------------------------------------------------------------------
@homepage.route('/homeAdmin')
def homeAdmin():
    conn = get_db_connection()
    if conn is None:
        flash("NO DB CONNECTION", category='error')
        return redirect(url_for('users.loginAdmin'))   

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM requests WHERE requestArchived=0")
        rows=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('admin/home_admin.html', email=session['accountEmail'], dbhtml=rows)
    except Error as e:
        flash(f'{e}', category='error')
        logout()

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
