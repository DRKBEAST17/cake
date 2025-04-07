from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database initialization
# Add after existing imports
from decimal import Decimal

# Add after existing database initialization
def init_db():
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    
    # Drop existing tables to rebuild schema
    c.execute('DROP TABLE IF EXISTS sales')
    c.execute('DROP TABLE IF EXISTS cakes')
    c.execute('DROP TABLE IF EXISTS categories')
    c.execute('DROP TABLE IF EXISTS customers')
    
    # Create tables with proper schema and constraints
    c.execute('''CREATE TABLE categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL UNIQUE,
                  description TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE customers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  phone TEXT NOT NULL UNIQUE,
                  email TEXT UNIQUE,
                  address TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE cakes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  category_id INTEGER NOT NULL,
                  description TEXT,
                  price REAL NOT NULL CHECK (price > 0),
                  quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT)''')
    
    c.execute('''CREATE TABLE sales
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  cake_id INTEGER NOT NULL,
                  customer_id INTEGER NOT NULL,
                  quantity INTEGER NOT NULL CHECK (quantity > 0),
                  unit_price REAL NOT NULL,
                  total REAL NOT NULL,
                  notes TEXT,
                  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (cake_id) REFERENCES cakes (id) ON DELETE RESTRICT,
                  FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE RESTRICT)''')

    # Create indexes for better performance
    c.execute('CREATE INDEX idx_cakes_category ON cakes(category_id)')
    c.execute('CREATE INDEX idx_sales_cake ON sales(cake_id)')
    c.execute('CREATE INDEX idx_sales_customer ON sales(customer_id)')
    c.execute('CREATE INDEX idx_sales_date ON sales(date)')

    # Add default categories
    default_categories = [
        ('Birthday Cakes', 'Special cakes for birthday celebrations'),
        ('Wedding Cakes', 'Elegant cakes for wedding ceremonies'),
        ('Anniversary Cakes', 'Romantic cakes for anniversary celebrations'),
        ('Custom Cakes', 'Personalized cakes as per customer requirements'),
        ('Cupcakes', 'Small, individual-sized cakes')
    ]
    c.executemany('INSERT INTO categories (name, description) VALUES (?, ?)', default_categories)
    
    conn.commit()
    conn.close()

# Add new routes after existing routes
@app.route('/categories')
def categories():
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    c.execute('SELECT * FROM categories')
    categories = c.fetchall()
    conn.close()
    return render_template('categories.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('cake_shop.db')
        c = conn.cursor()
        c.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        flash('Category added successfully!')
        return redirect(url_for('categories'))
    return render_template('add_category.html')

@app.route('/customers')
def customers():
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    c.execute('SELECT * FROM customers')
    customers = c.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        
        conn = sqlite3.connect('cake_shop.db')
        c = conn.cursor()
        c.execute('''INSERT INTO customers (name, phone, email, address) 
                     VALUES (?, ?, ?, ?)''', (name, phone, email, address))
        conn.commit()
        conn.close()
        flash('Customer added successfully!')
        return redirect(url_for('customers'))
    return render_template('add_customer.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    c.execute('''SELECT c.id, c.name, cat.name, c.price, c.quantity 
                 FROM cakes c 
                 LEFT JOIN categories cat ON c.category_id = cat.id''')
    cakes = c.fetchall()
    conn.close()
    return render_template('inventory.html', cakes=cakes)

@app.route('/edit_cake/<int:cake_id>', methods=['GET', 'POST'])
def edit_cake(cake_id):
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        category_id = request.form['category_id']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        
        c.execute('''UPDATE cakes 
                     SET name=?, category_id=?, price=?, quantity=?
                     WHERE id=?''',
                 (name, category_id, price, quantity, cake_id))
        conn.commit()
        flash('Cake updated successfully!')
        return redirect(url_for('inventory'))
    
    c.execute('SELECT * FROM cakes WHERE id=?', (cake_id,))
    cake = c.fetchone()
    c.execute('SELECT id, name FROM categories')
    categories = c.fetchall()
    conn.close()
    return render_template('edit_cake.html', cake=cake, categories=categories)

@app.route('/add_cake', methods=['GET', 'POST'])
def add_cake():
    if request.method == 'POST':
        name = request.form['name']
        category_id = int(request.form['category_id'])
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        
        conn = sqlite3.connect('cake_shop.db')
        c = conn.cursor()
        c.execute('INSERT INTO cakes (name, category_id, price, quantity) VALUES (?, ?, ?, ?)',
                 (name, category_id, price, quantity))
        conn.commit()
        conn.close()
        flash('Cake added successfully!')
        return redirect(url_for('inventory'))
    
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM categories')
    categories = c.fetchall()
    conn.close()
    return render_template('add_cake.html', categories=categories)

@app.route('/new_sale', methods=['GET', 'POST'])
def new_sale():
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        cake_id = int(request.form['cake_id'])
        customer_id = int(request.form['customer_id'])
        quantity = int(request.form['quantity'])
        
        # Get cake price and verify cake exists
        c.execute('SELECT price FROM cakes WHERE id = ?', (cake_id,))
        result = c.fetchone()
        if result is None:
            conn.close()
            flash('Error: Cake not found!')
            return redirect(url_for('new_sale'))
            
        cake_price = result[0]
        
        # Calculate total
        total = cake_price * quantity
        
        # Record sale with unit_price
        c.execute('''INSERT INTO sales 
                    (cake_id, customer_id, quantity, unit_price, total, date)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))''',
                 (cake_id, customer_id, quantity, cake_price, total))
        
        # Update cake quantity
        c.execute('UPDATE cakes SET quantity = quantity - ? WHERE id = ?',
                 (quantity, cake_id))
        
        conn.commit()
        flash('Sale recorded successfully!')
        return redirect(url_for('sales'))
    
    # Get cakes and customers for the form
    c.execute('SELECT id, name, price, quantity FROM cakes WHERE quantity > 0')
    cakes = c.fetchall()
    c.execute('SELECT id, name FROM customers')
    customers = c.fetchall()
    conn.close()
    
    return render_template('new_sale.html', cakes=cakes, customers=customers)

@app.route('/sales')
def sales():
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            sales.id,
            sales.date,
            cakes.name as cake_name,
            customers.name as customer_name,
            customers.phone as customer_phone,
            customers.email as customer_email,
            sales.quantity,
            sales.total,
            cakes.price as unit_price
        FROM sales
        JOIN cakes ON sales.cake_id = cakes.id
        JOIN customers ON sales.customer_id = customers.id
        ORDER BY sales.date DESC
    ''')
    
    columns = ['id', 'date', 'cake_name', 'customer_name', 'quantity', 'total']
    sales = [dict(zip(columns, row)) for row in c.fetchall()]
    
    conn.close()
    return render_template('sales.html', sales=sales)

@app.route('/customer_history/<int:customer_id>')
def customer_history(customer_id):
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    c.execute('''SELECT sales.date, cakes.name, sales.quantity, 
                 sales.total_with_tax, customers.name
                 FROM sales 
                 JOIN cakes ON sales.cake_id = cakes.id
                 JOIN customers ON sales.customer_id = customers.id
                 WHERE sales.customer_id = ?
                 ORDER BY sales.date DESC''', (customer_id,))
    history = c.fetchall()
    conn.close()
    return render_template('customer_history.html', history=history)

# Delete the following route
@app.route('/tax_report')
def tax_report():
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    c.execute('''SELECT strftime('%Y-%m', date) as month,
                 SUM(subtotal) as total_sales,
                 SUM(gst) as total_gst,
                 SUM(total_with_tax) as total_with_tax
                 FROM sales
                 GROUP BY strftime('%Y-%m', date)
                 ORDER BY month DESC''')
    reports = c.fetchall()
    conn.close()
    return render_template('tax_report.html', reports=reports)

@app.route('/receipt/<int:sale_id>')
def receipt(sale_id):
    conn = sqlite3.connect('cake_shop.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            sales.id,
            sales.date,
            cakes.name as cake_name,
            customers.name as customer_name,
            customers.phone as customer_phone,
            customers.email as customer_email,
            sales.quantity,
            sales.total,
            cakes.price as unit_price
        FROM sales
        JOIN cakes ON sales.cake_id = cakes.id
        JOIN customers ON sales.customer_id = customers.id
        WHERE sales.id = ?
    ''', (sale_id,))
    
    result = c.fetchone()
    
    if result is None:
        conn.close()
        flash('Receipt not found!')
        return redirect(url_for('sales'))
    
    columns = ['id', 'date', 'cake_name', 'customer_name', 'customer_phone', 
               'customer_email', 'quantity', 'total', 'unit_price']
    sale = dict(zip(columns, result))
    
    conn.close()
    return render_template('receipt.html', sale=sale)

# Make sure to call init_db() when the application starts
if __name__ == '__main__':
    init_db()
    app.run(debug=True)