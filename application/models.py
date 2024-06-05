from .database import db

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    mob = db.Column(db.Integer, unique=True)
    password = db.Column(db.String)
    isAdmin = db.Column(db.Integer)

class items(db.Model):
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    qty = db.Column(db.Integer)
    dom = db.Column(db.Date)
    doe = db.Column(db.Date)
    price = db.Column(db.Integer)
    category = db.relationship("categories", secondary="categoryOfItem")
    unit = db.Column(db.String)

class categories(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    catName = db.Column(db.String)
    items = db.relationship("items", secondary="categoryOfItem")

class categoryOfItem(db.Model):
    __tablename__ = 'categoryOfItem'
    category_id = db.Column(db.Integer,   db.ForeignKey("categories.category_id"), primary_key=True, nullable=False)
    item_id = db.Column(db.Integer,  db.ForeignKey("items.item_id"), primary_key=True, nullable=False) 
    
class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)

    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
