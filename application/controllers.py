from flask import Flask, request, flash, redirect, url_for, session, flash, make_response, jsonify
from flask import render_template
from flask import current_app as app
from sqlalchemy import func
from application.models import *
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from collections import defaultdict


@app.route("/", methods=["GET", "POST"])
def home():  
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = User.query.filter_by(username=username, password=password, isAdmin=1).first()
        user = User.query.filter_by(username=username, password=password, isAdmin=0).first()
        if admin: 
            flash('Login successful!', 'success')
            session['user_id'] = admin.user_id
            return redirect(url_for('dashboard'))
        
        elif user:  
            flash('Login successful!', 'success')
            session['user_id'] = user.user_id
            return redirect(url_for('shop'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/adminLogin', methods=['GET', 'POST'])
def adminLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = User.query.filter_by(username=username, password=password, isAdmin=1).first()
        user = User.query.filter_by(username=username, password=password, isAdmin=0).first()
        session['username'] = username
        if admin: 
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        
        elif user:  
            flash('Login successful!', 'success')
            return redirect(url_for('shop'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('adminLogin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        mob = request.form['mob']
        isadmin = False 

        user = User(username=username, email=email, mob=mob, password=password, isAdmin=isadmin)
        db.session.add(user)
        db.session.commit()
        
        flash('Signup successful! You can now login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signupUser.html')

@app.route('/signupAdmin', methods=['GET', 'POST'])
def signupAdmin():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        mob = request.form['mob']

        secret_key = request.form['secret_key']
        if secret_key == "Trust me, I am an admin":
            isadmin = True 
        else:
            return render_template('error.html', message="Secret Key Mismatch")

        user = User(username=username, email=email, mob=mob, password=password, isAdmin=isadmin)
        db.session.add(user)
        db.session.commit()
        
        flash('Signup successful! You can now login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signupAdmin.html')


@app.route('/logout')
def logout():

    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/shop', methods=['GET', 'POST'])
def shop():
    cart_cookie = request.cookies.get('cart')
    cart = {}
    if cart_cookie:
        cart = {int(item_id): int(qty) for item_id, qty in map(str.split, cart_cookie.split(','))}

    categorylist = categories.query.all()

    return render_template('shop.html', categorylist=categorylist, cart=cart)

@app.route('/dashboard')
def dashboard():
    categorylist = categories.query.all()
    itemlist = items.query.all()
    return render_template('dashboard.html', categories=categorylist, items=itemlist)

@app.route('/add_category', methods=['POST'])
def add_category():
    category_name = request.form['category_name']
    if category_name.strip() != '':
        category = categories(catName=category_name)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully.', 'success')
    else:
        flash('Category name cannot be empty.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/add_item', methods=['POST'])
def add_item():
    item_name = request.form['item_name']
    category_id = request.form['category']
    quantity = request.form['quantity']
    manufacture_date = request.form['manufacture_date']
    expiry_date = request.form['expiry_date']
    price = request.form['price']
    unit = request.form['unit']

    manufacture_date = datetime.strptime(manufacture_date, '%Y-%m-%d').date()
    expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()

    if item_name.strip() != '' and quantity.strip() != '' and price.strip() != '':
        item = items(name=item_name, qty=quantity, dom=manufacture_date,
                    doe=expiry_date, price=price, unit=unit)
        item.category.append(categories.query.get(category_id))
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully.', 'success')
    else:
        flash('Item name, quantity, and price cannot be empty.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_category/<int:category_id>', methods=['GET'])
def delete_category(category_id):
    category = categories.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_item/<int:item_id>', methods=['GET'])
def delete_item(item_id):
    item = items.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/edit_category/<int:category_id>', methods=['GET'])
def edit_category(category_id):
    category = categories.query.get_or_404(category_id)
    return render_template('edit_category.html', category=category)

@app.route('/update_category/<int:category_id>', methods=['POST'])
def update_category(category_id):
    category = categories.query.get_or_404(category_id)
    category_name = request.form['category_name']

    if category_name.strip() != '':
        category.catName = category_name
        db.session.commit()
        flash('Category updated successfully.', 'success')
    else:
        flash('Category name cannot be empty.', 'error')

    return redirect(url_for('dashboard'))

@app.route('/edit_item/<int:item_id>', methods=['GET'])
def edit_item(item_id):
    itemlist = items.query.get_or_404(item_id)
    categorylist = categories.query.all()
    return render_template('edit_item.html', item=itemlist, categories=categorylist)

@app.route('/update_item/<int:item_id>', methods=['POST'])
def update_item(item_id):
    item = items.query.get_or_404(item_id)
    item_name = request.form['item_name']
    category_id = request.form['category']
    quantity = request.form['qty']
    manufacture_date = request.form['dom']
    expiry_date = request.form['doe']
    price = request.form['price']

    # Convert date strings to Python date objects
    manufacture_date = datetime.strptime(manufacture_date, '%Y-%m-%d').date()
    expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()

    if item_name.strip() != '' and quantity.strip() != '' and price.strip() != '':
        # Update the items table
        item.name = item_name
        item.qty = quantity
        item.dom = manufacture_date
        item.doe = expiry_date
        item.price = price

        selected_category = categories.query.get(category_id)
        if selected_category:
            item.category.clear()
            item.category.append(selected_category)

            db.session.commit()
            flash('Item updated successfully.', 'success')
        else:
            flash('Selected category not found.', 'error')
    else:
        flash('Item name, quantity, and price cannot be empty.', 'error')

    return redirect(url_for('dashboard'))




@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('query')
    if search_query:
        search_query = f'%{search_query}%' 
        categorylist = categories.query.filter(categories.catName.ilike(f'%{search_query}%')).all()
        itemlist = items.query.filter(items.name.ilike(f'%{search_query}%')).all()
    else:
        categorylist = categories.query.all()
        itemlist = items.query.all()

    return render_template('searchresults.html', categorylist=categorylist, itemlist=itemlist)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = int(request.form['item_id'])
    quantity = int(request.form['quantity'])

    item = items.query.get(item_id)

    if not item:
        return render_template('error.html', error_message='Item not found.')

    if quantity > item.qty:
        return render_template('error.html', error_message='Not enough quantity in stock.')

    cart_cookie = request.cookies.get('cart')
    cart = {}

    if cart_cookie:
        cart = {int(item_id): int(qty) for item_id, qty in map(str.split, cart_cookie.split(','))}

    cart[item_id] = cart.get(item_id, 0) + quantity

    cart_data = ','.join([f"{item_id} {qty}" for item_id, qty in cart.items()])
    response = make_response(redirect(url_for('shop')))
    response.set_cookie('cart', cart_data)

    flash('Item added to cart successfully.', 'success')
    return response


@app.route('/cart')
def view_cart():
    user_id = session.get('user_id')
    cart_cookie = request.cookies.get('cart')
    cart = {} 

    if cart_cookie:
        cart = {int(item_id): int(qty) for item_id, qty in map(str.split, cart_cookie.split(','))}

    items_in_cart = items.query.filter(items.item_id.in_(cart.keys())).all()

    total_price = sum(item.price * cart[item.item_id] for item in items_in_cart)

    return render_template('cart.html', cart=cart, items_in_cart=items_in_cart, total_price=total_price)


@app.route('/update_cart', methods=['POST'])
def update_cart():
    item_id = int(request.form['item_id'])
    quantity = int(request.form['quantity'])

    item = items.query.get(item_id)

    if not item:
        return render_template('error.html', error_message='Item not found.')

    if quantity > item.qty:
        return render_template('error.html', error_message='Not enough quantity in stock.')

    cart_cookie = request.cookies.get('cart')
    cart = {}

    if cart_cookie:
  
        cart = {int(item_id): int(qty) for item_id, qty in map(str.split, cart_cookie.split(','))}

    if quantity > 0:
        cart[item_id] = quantity
    else:
        cart.pop(item_id, None)

    cart_data = ','.join([f"{item_id} {qty}" for item_id, qty in cart.items()])
    response = make_response(redirect(url_for('view_cart')))
    response.set_cookie('cart', cart_data)

    flash('Cart updated successfully.', 'success')
    return response


@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    cart_cookie = request.cookies.get('cart')
    cart = {}

    if cart_cookie:
        cart = {int(item_id): int(qty) for item_id, qty in map(str.split, cart_cookie.split(','))}

    cart.pop(item_id, None)

    cart_data = ','.join([f"{item_id} {qty}" for item_id, qty in cart.items()])
    response = make_response(redirect(url_for('view_cart')))
    response.set_cookie('cart', cart_data)

    flash('Item removed from cart successfully.', 'success')
    return response

@app.route('/checkout', methods=['POST'])
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        return render_template('errorrrrr.html', error_message='User not logged in or authenticated.')

    cart_data = request.cookies.get('cart')
    if cart_data:
        cart = {}
        itemlist = cart_data.split(',')
        for item in itemlist:
            item_id, quantity = item.split(' ')
            cart[int(item_id)] = int(quantity)
    else:
        cart = {}

    item_ids = list(cart.keys())
    items_in_cart = items.query.filter(items.item_id.in_(item_ids)).all()

    for item in items_in_cart:
        if item.qty < cart[item.item_id]:
            return render_template('error.html', error_message=f"Not enough quantity in stock for {item.name}.")

    total_price = 0.0
    for item in items_in_cart:
        total_price += item.price * cart[item.item_id]

    order = Order(user_id=user_id, total_price=total_price, order_date=datetime.now())
    db.session.add(order)
    db.session.flush()

    for item_id, quantity in cart.items():
        item = items.query.get(item_id)
        item.qty -= quantity
        db.session.add(item)

        order_item = OrderItem(order_id=order.order_id, item_id=item_id, quantity=quantity)
        db.session.add(order_item)

    db.session.commit()

    response = make_response(redirect(url_for('shop')))
    response.delete_cookie('cart')
    return response

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']

        user = User.query.get(user_id)
        previous_orders = Order.query.filter_by(user_id=user_id).all()

        order_items_list = []
        for order in previous_orders:
            order_items = []
            for order_item in order.items: #doesnt seem to work as of now
                item = items.query.get(order_item.item_id)
                item_details = {
                    'name': item.name,
                    'quantity': order_item.quantity,
                    'price': item.price
                }
                order_items.append(item_details)

            order_details = {
                'order_id': order.order_id,
                'order_date': order.order_date.strftime('%Y-%m-%d %H:%M'),
                'total_price': order.total_price,
                'items': order_items
            }

            order_items_list.append(order_details)

        return render_template('profile.html', user=user, orders=order_items_list)
    else:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('login'))


@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    username = request.form['username']
    email = request.form['email']
    mob = request.form['mob']

    user_id = session.get('user_id')

    user = User.query.get(user_id)
    user.username = username
    user.email = email
    user.mob = mob

    db.session.commit()

    flash('Profile updated successfully.', 'success')
    return redirect(url_for('profile'))

@app.route('/insights')
def insights():
    if 'user_id' in session :
        category_data = db.session.query(categories.catName, db.func.sum(items.qty).label('total_qty')).\
            join(categories.items).group_by(categories.catName).all()

        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(category_data, columns=['Category', 'Total Quantity'])

        # Generate the pie chart
        plt.figure(figsize=(8, 6))
        plt.pie(df['Total Quantity'], labels=df['Category'], autopct='%1.1f%%')
        plt.title('Total Quantity of Items in Each Category')

        # Save the chart to a BytesIO buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()

        orders = Order.query.all()

        total_price_by_date = defaultdict(float)
        for order in orders:
            date = order.order_date.date()
            total_price_by_date[date] += order.total_price

        dates = list(total_price_by_date.keys())
        total_prices = list(total_price_by_date.values())

        chart_data_bar = {
            'labels': [str(date) for date in dates],
            'datasets': [
                {
                    'label': 'Total Price',
                    'data': total_prices,
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                }
            ]
        }



        return render_template('insights.html', chart_data_pie=chart_data, chart_data_bar=chart_data_bar)
    else:
        flash('Access denied. You must be logged in as an admin to view this page.', 'danger')
        return redirect(url_for('login'))

# API routes:
# API endpoint to create a new item
@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.get_json()
    name = data['name']
    qty = data['qty']
    dom = data['dom']
    doe = data['doe']
    price = data['price']
    unit = data['unit']

    new_item = items(name=name, qty=qty, dom=dom, doe=doe, price=price, unit=unit)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({'message': 'Item created successfully'}), 201

# API endpoint to get all items
@app.route('/api/items', methods=['GET'])
def get_all_items():
    all_items = items.query.all()
    result = [{'name': item.name, 'qty': item.qty, 'dom': item.dom, 'doe': item.doe, 'price': item.price, 'unit': item.unit} for item in all_items]
    return jsonify(result)

# API endpoint to update an item
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item_api(item_id):
    data = request.get_json()
    item = items.query.get(item_id)

    if item:
        item.name = data['name']
        item.qty = data['qty']
        item.dom = data['dom']
        item.doe = data['doe']
        item.price = data['price']
        item.unit = data['unit']

        db.session.commit()
        return jsonify({'message': 'Item updated successfully'}), 200
    else:
        return jsonify({'message': 'Item not found'}), 404

# API endpoint to delete an item
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item_api(item_id):
    item = items.query.get(item_id)

    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'}), 200
    else:
        return jsonify({'message': 'Item not found'}), 404

# API endpoint to create a new category
@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    catName = data['catName']

    new_category = categories(catName=catName)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'Category created successfully'}), 201

# API endpoint to get all categories
@app.route('/api/categories', methods=['GET'])
def get_all_categories():
    all_categories = categories.query.all()
    result = [{'catName': category.catName} for category in all_categories]
    return jsonify(result)

# API endpoint to update a category
@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category_api(category_id):
    data = request.get_json()
    category = categories.query.get(category_id)

    if category:
        category.catName = data['catName']

        db.session.commit()
        return jsonify({'message': 'Category updated successfully'}), 200
    else:
        return jsonify({'message': 'Category not found'}), 404

# API endpoint to delete a category
@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category_api(category_id):
    category = categories.query.get(category_id)

    if category:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'}), 200
    else:
        return jsonify({'message': 'Category not found'}), 404