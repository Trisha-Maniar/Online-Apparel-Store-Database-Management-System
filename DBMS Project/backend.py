import os
import re
from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', ''),
    'database': os.getenv('DB_NAME', 'online_apparel_store_dbms'),
    'autocommit': True,
    'cursorclass': pymysql.cursors.DictCursor
}

app = Flask(__name__, static_folder='.', static_url_path='/')
app.secret_key = os.getenv('SECRET_KEY', 'change-me')
CORS(app)

def get_db():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print('DB connect error:', e)
        return None

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_input(data, required_fields):
    """Validate required fields are present and not empty"""
    for field in required_fields:
        if not data.get(field) or not str(data.get(field)).strip():
            return False, f'{field} is required'
    return True, None

# Note: Using existing 'customer' table from database schema
# No need to create users table

# ---------- Auth ----------
@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    name = data.get('name', '').strip() if data.get('name') else ''
    email = data.get('email', '').strip() if data.get('email') else ''
    password = data.get('password', '')
    
    # Validation
    valid, error_msg = validate_input(data, ['email', 'password'])
    if not valid:
        return jsonify({'error': error_msg}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor()
    # Hash password for security (storing hashed version)
    phash = generate_password_hash(password)
    try:
        # Insert into customer table with hashed password
        # Note: Database has Password column (plain text), but we'll store hash for security
        # If you need plain text, change phash to password
        cur.execute("""
            INSERT INTO customer (Name, Email, Password, Date_Registered) 
            VALUES (%s, %s, %s, CURDATE())
        """, (name, email, phash))
        customer_id = cur.lastrowid
        conn.commit()
    except pymysql.IntegrityError:
        cur.close(); conn.close()
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        cur.close(); conn.close()
        print(f"Signup error: {e}")
        return jsonify({'error': 'Registration failed'}), 500
    cur.close(); conn.close()
    return jsonify({'ok': True, 'customer_id': customer_id})

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip() if data.get('email') else ''
    password = data.get('password', '')
    
    if not (email and password):
        return jsonify({'error': 'Email and password required'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor()
    try:
        # Query customer table
        cur.execute("SELECT Customer_ID, Name, Email, Password FROM customer WHERE Email=%s", (email,))
        u = cur.fetchone()
    except Exception as e:
        cur.close(); conn.close()
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500
    
    cur.close(); conn.close()
    
    if not u:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check password - try both hashed (new users) and plain text (existing users)
    password_valid = False
    stored_password = u['Password']
    
    # Try checking as hash first (for new registrations)
    try:
        password_valid = check_password_hash(stored_password, password)
    except:
        # If not a hash, check as plain text (for existing database entries)
        password_valid = (stored_password == password)
    
    if not password_valid:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    session['user_id'] = u['Customer_ID']
    session['user_email'] = u['Email']
    session['user_name'] = u.get('Name') or ''
    return jsonify({'ok': True, 'user': {'id': u['Customer_ID'], 'email': u['Email'], 'name': u.get('Name')}})

@app.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok':True})

@app.route('/auth/me')
def auth_me():
    if 'user_id' in session:
        return jsonify({'logged_in':True, 'user': {'id':session.get('user_id'), 'email':session.get('user_email'), 'name':session.get('user_name')}})
    return jsonify({'logged_in':False})

# ---------- Products ----------
@app.route('/api/products')
def api_products():
    conn = get_db()
    if not conn:
        return jsonify({'error':'db'}), 500
    cur = conn.cursor()
    cur.execute("SELECT Product_ID, Product_Name, Description, Price, Discount, Brand FROM product ORDER BY Product_ID DESC LIMIT 200")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/products/<int:pid>')
def api_product(pid):
    conn = get_db()
    if not conn:
        return jsonify({'error':'db'}), 500
    cur = conn.cursor()
    cur.execute("SELECT * FROM product WHERE Product_ID=%s", (pid,))
    r = cur.fetchone()
    cur.close(); conn.close()
    if not r:
        return jsonify({'error':'not found'}), 404
    return jsonify(r)

# ---------- Cart ----------
@app.route('/api/cart', methods=['GET'])
def api_cart_get():
    user_id = session.get('user_id')
    guest = request.args.get('guest_id')
    if not user_id and not guest:
        return jsonify({'error':'login required or pass guest_id'}), 401
    cust = user_id or guest
    conn = get_db()
    if not conn:
        return jsonify({'error':'db'}), 500
    cur = conn.cursor()
    cur.execute("SELECT c.Product_ID, c.Quantity, p.Product_Name, p.Price FROM cart c JOIN product p ON p.Product_ID=c.Product_ID WHERE c.Customer_ID=%s", (cust,))
    items = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(items)

@app.route('/api/cart/add', methods=['POST'])
def api_cart_add():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    qty = int(data.get('quantity', 1))
    guest = data.get('guest_id')
    user_id = session.get('user_id')
    
    if not product_id:
        return jsonify({'error': 'product_id required'}), 400
    
    if qty < 1:
        return jsonify({'error': 'quantity must be at least 1'}), 400
    
    if not user_id and not guest:
        return jsonify({'error': 'login required or provide guest_id'}), 401
    
    cust = user_id or guest
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor()
    try:
        # Check if product exists
        cur.execute("SELECT Product_ID FROM product WHERE Product_ID=%s", (product_id,))
        if not cur.fetchone():
            cur.close(); conn.close()
            return jsonify({'error': 'Product not found'}), 404
        
        cur.execute("SELECT Quantity FROM cart WHERE Customer_ID=%s AND Product_ID=%s", (cust, product_id))
        r = cur.fetchone()
        if r:
            newq = r[0] + qty
            cur.execute("UPDATE cart SET Quantity=%s WHERE Customer_ID=%s AND Product_ID=%s", (newq, cust, product_id))
        else:
            cur.execute("INSERT INTO cart (Customer_ID, Product_ID, Quantity, Added_Date) VALUES (%s,%s,%s,NOW())", (cust, product_id, qty))
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close(); conn.close()
        print(f"Cart add error: {e}")
        return jsonify({'error': 'Failed to add to cart'}), 500
    
    cur.close(); conn.close()
    return jsonify({'ok': True})

@app.route('/api/cart/remove', methods=['POST'])
def api_cart_remove():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    guest = data.get('guest_id')
    user_id = session.get('user_id')
    if not product_id:
        return jsonify({'error':'product_id required'}), 400
    if not user_id and not guest:
        return jsonify({'error':'login required or provide guest_id'}), 401
    cust = user_id or guest
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE Customer_ID=%s AND Product_ID=%s", (cust, product_id))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'ok':True})

# ---------- Checkout / Orders ----------
@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    data = request.get_json() or {}
    payment_method = data.get('payment_method','UPI')
    guest = data.get('guest_id')
    user_id = session.get('user_id')
    if not user_id and not guest:
        return jsonify({'error':'login required or provide guest_id'}), 401
    cust = user_id or guest
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT c.Product_ID, c.Quantity, p.Price FROM cart c JOIN product p ON p.Product_ID=c.Product_ID WHERE c.Customer_ID=%s", (cust,))
    items = cur.fetchall()
    if not items:
        cur.close(); conn.close(); return jsonify({'error':'cart empty'}), 400
    total = sum(float(it['Price'])*it['Quantity'] for it in items)
    cur2 = conn.cursor()
    try:
        # Insert order - Payment_Status will be set by trigger based on Payment_Method
        cur2.execute("""
            INSERT INTO orders (Customer_ID, Order_Date, Total_Amount, Payment_Method, Order_Status, Shipping_Address) 
            VALUES (%s, NOW(), %s, %s, 'Processing', 'Default Address')
        """, (cust, total, payment_method))
        order_id = cur2.lastrowid
        
        for it in items:
            # Insert order item
            cur2.execute("""
                INSERT INTO order_item (Order_ID, Product_ID, Quantity, Price_at_Purchase) 
                VALUES (%s, %s, %s, %s)
            """, (order_id, it['Product_ID'], it['Quantity'], float(it['Price'])*it['Quantity']))
            
            # Update inventory - handle multiple warehouses by updating the first available stock
            # Get the Stock_ID with available quantity
            cur3 = conn.cursor()
            cur3.execute("""
                SELECT Stock_ID, Quantity_Available 
                FROM inventory 
                WHERE Product_ID=%s AND Quantity_Available >= %s 
                ORDER BY Quantity_Available DESC 
                LIMIT 1
            """, (it['Product_ID'], it['Quantity']))
            stock = cur3.fetchone()
            cur3.close()
            
            if stock:
                # Update specific warehouse stock
                cur2.execute("""
                    UPDATE inventory 
                    SET Quantity_Available = Quantity_Available - %s 
                    WHERE Stock_ID=%s
                """, (it['Quantity'], stock['Stock_ID']))
            else:
                # If no single warehouse has enough, update the one with most stock
                cur3 = conn.cursor()
                cur3.execute("""
                    SELECT Stock_ID 
                    FROM inventory 
                    WHERE Product_ID=%s 
                    ORDER BY Quantity_Available DESC 
                    LIMIT 1
                """, (it['Product_ID'],))
                stock_fallback = cur3.fetchone()
                cur3.close()
                if stock_fallback:
                    cur2.execute("""
                        UPDATE inventory 
                        SET Quantity_Available = GREATEST(0, Quantity_Available - %s) 
                        WHERE Stock_ID=%s
                    """, (it['Quantity'], stock_fallback['Stock_ID']))
        
        # Insert payment - Payment_Status will be set by trigger
        cur2.execute("""
            INSERT INTO payment (Order_ID, Payment_Date, Payment_Method, Amount_Paid, Transaction_ID) 
            VALUES (%s, NOW(), %s, %s, CONCAT('TXN', FLOOR(RAND()*10000000)))
        """, (order_id, payment_method, total))
        
        # Clear cart
        cur2.execute("DELETE FROM cart WHERE Customer_ID=%s", (cust,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close(); cur2.close(); conn.close()
        print(f"Checkout error: {e}")
        return jsonify({'error': 'Checkout failed: ' + str(e)}), 500
    
    cur.close(); cur2.close(); conn.close()
    return jsonify({'ok':True, 'order_id': order_id, 'total': float(total)})

@app.route('/api/orders')
def api_orders():
    user_id = session.get('user_id')
    guest = request.args.get('guest_id')
    if not user_id and not guest:
        return jsonify({'error':'login required or guest_id'}), 401
    cust = user_id or guest
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE Customer_ID=%s ORDER BY Order_Date DESC", (cust,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

# Serve frontend static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)

