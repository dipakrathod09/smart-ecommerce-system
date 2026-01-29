from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', name=session['user_name'])


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )

        conn.commit()
        cur.close()
        conn.close()

        return "Registration Successful"

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['role'] = user[4]
            return redirect(url_for('dashboard'))
        else:
            return "Invalid email or password"

    return render_template('login.html')

@app.route('/products')
def products():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, description, price, stock FROM products")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    products_list = []
    for row in rows:
        products_list.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
            "stock": row[4]
        })

    return render_template('products.html', products=products_list)

@app.route('/admin/products')
def admin_products():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    products = []
    for r in rows:
        products.append({
            "id": r[0],
            "name": r[1],
            "price": r[2],
            "stock": r[3]
        })

    return render_template('admin_products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        desc = request.form['description']

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products (name, price, stock, description) VALUES (%s, %s, %s, %s)",
            (name, price, stock, desc)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('admin_products'))

    return render_template('add_product.html')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute(
            "UPDATE products SET name=%s, price=%s, stock=%s WHERE id=%s",
            (request.form['name'], request.form['price'], request.form['stock'], product_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('admin_products'))

    cur.execute("SELECT id, name, price, stock FROM products WHERE id=%s", (product_id,))
    p = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('edit_product.html', p=p)

@app.route('/admin/products/delete/<int:product_id>')
def delete_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('admin_products'))


@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price FROM products WHERE id=%s", (product_id,))
    product = cur.fetchone()
    cur.close()
    conn.close()

    if not product:
        return redirect(url_for('products'))

    cart = session.get('cart', {})

    pid = str(product[0])
    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {
            'name': product[1],
            'price': float(product[2]),
            'quantity': 1
        }

    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('cart.html', cart=session.get('cart', {}))

@app.route('/remove-from-cart/<product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(product_id, None)
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart = session.get('cart')
    if not cart:
        return redirect(url_for('products'))

    if request.method == 'POST':
        user_id = session['user_id']
        total = sum(item['price'] * item['quantity'] for item in cart.values())

        conn = get_connection()
        cur = conn.cursor()

        # Insert order
        cur.execute(
            "INSERT INTO orders (user_id, total_amount) VALUES (%s, %s) RETURNING id",
            (user_id, total)
        )
        order_id = cur.fetchone()[0]

        # Insert order items
        for item in cart.values():
            cur.execute(
                "INSERT INTO order_items (order_id, product_name, price, quantity) VALUES (%s, %s, %s, %s)",
                (order_id, item['name'], item['price'], item['quantity'])
            )

        conn.commit()
        cur.close()
        conn.close()

        # Clear cart
        session.pop('cart', None)

        return redirect(url_for('order_success', order_id=order_id))

    return render_template('checkout.html', cart=cart)

@app.route('/order-success/<int:order_id>')
def order_success(order_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('order_success.html', order_id=order_id)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
