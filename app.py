from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)

# ADMIN LOGIN DETAILS
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# PRODUCT TABLE
class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    price = db.Column(db.Integer)

    image = db.Column(db.String(300))

# USER TABLE
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    password = db.Column(db.String(100))

# CART TABLE
class Cart(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    product_id = db.Column(db.Integer)

    product_name = db.Column(db.String(100))

    price = db.Column(db.Integer)

# HOME PAGE
@app.route('/')
def home():

    search = request.args.get('search')

    if search:

        products = Product.query.filter(
            Product.name.contains(search)
        ).all()

    else:

        products = Product.query.all()

    return render_template(
        'index.html',
        products=products
    )

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User(
            username=username,
            password=password
        )

        db.session.add(user)

        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session['username'] = username

            return redirect('/')

        return "Invalid Credentials"

    return render_template('login.html')

# LOGOUT
@app.route('/logout')
def logout():

    session.pop('username', None)

    session.pop('admin', None)

    return redirect('/')

# ADMIN LOGIN
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session['admin'] = True

            return redirect('/admin')

        return "Invalid Admin Credentials"

    return render_template('admin_login.html')

# ADMIN PAGE
@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if 'admin' not in session:

        return redirect('/admin-login')

    if request.method == 'POST':

        name = request.form['name']

        price = int(request.form['price'])

        image = request.form['image']

        product = Product(
            name=name,
            price=price,
            image=image
        )

        db.session.add(product)

        db.session.commit()

        return redirect('/admin')

    products = Product.query.all()

    return render_template(
        'admin.html',
        products=products
    )

# DELETE PRODUCT
@app.route('/delete-product/<int:id>')
def delete_product(id):

    if 'admin' not in session:

        return redirect('/admin-login')

    product = Product.query.get(id)

    if product:

        Cart.query.filter_by(
            product_id=product.id
        ).delete()

        db.session.delete(product)

        db.session.commit()

    return redirect('/admin')

# ADD TO CART
@app.route('/cart/<int:id>')
def cart(id):

    if 'username' not in session:

        return redirect('/login')

    product = Product.query.get(id)

    if not product:

        return redirect('/')

    item = Cart(
        username=session['username'],
        product_id=product.id,
        product_name=product.name,
        price=product.price
    )

    db.session.add(item)

    db.session.commit()

    return redirect('/view-cart')

# VIEW CART
@app.route('/view-cart')
def view_cart():

    if 'username' not in session:

        return redirect('/login')

    items = Cart.query.filter_by(
        username=session['username']
    ).all()

    return render_template(
        'cart.html',
        items=items
    )

# RUN APP
if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    app.run(debug=True)