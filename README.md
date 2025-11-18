Online-Apparel-Store-Database-Management-System

A full-stack e-commerce application for an online apparel store built with Flask (Python) backend and vanilla JavaScript frontend, using MySQL database.

---

Features

- User Authentication: Sign up, login, and logout with secure password hashing
- Product Browsing: View products with details, prices, and descriptions
- Shopping Cart: Add/remove items, view cart contents
- Guest Shopping: Shop without account (uses localStorage for guest sessions)
- Order Management: Place orders and view order history
- Inventory Management: Automatic inventory updates on checkout

---

Project Structure:

DBMS Project
backend.py              # Flask backend server
init_database.py        # Database initialization script
index.html             # Home page (product listing)
login.html             # Login page
signup.html            # Registration page
product.html           # Product detail page
cart.html              # Shopping cart
checkout.html          # Checkout page
orders.html            # Order history
common.js              # Shared JavaScript utilities
home.js                # Home page JavaScript
styles.css             # Stylesheet
README.md              # This file

---

Setup Instructions:

Prerequisites:

- Python 3.7+
- MySQL Server
- pip (Python package manager)

1. Install Dependencies

bash
pip install flask flask-cors python-dotenv mysql-connector-python werkzeug

2. Configure Database

Create a .env file in the project root with your database credentials:

env:
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASS=your_password
DB_NAME=online_apparel_store_dbms
SECRET_KEY=your-secret-key-here

3. Initialize Database

Run the database initialization script to create all required tables:

bash
python init_database.py

This will:
- Create the database if it doesn't exist
- Create all required tables (users, product, cart, orders, etc.)
- Optionally insert sample products for testing

4. Start the Server

bash
python backend.py

The server will start on http://localhost:5000 (default Flask port).

5. Access the Application

Open your browser and navigate to:

http://localhost:5000

---

Database Schema:

Tables

- users: User accounts and authentication
- product: Product catalog
- inventory: Product stock levels
- cart: Shopping cart items
- orders: Order records
- order_item: Individual items in orders
- payment: Payment transaction records

API Endpoints

Authentication
- POST/auth/signup - Create new account
- POST/auth/login - Login user
- POST/auth/logout - Logout user
- GET/auth/me - Get current user session

Products
- GET/api/products - List all products
- GET/api/products/<id> - Get product details

Cart
- GET/api/cart?guest_id=<id> - Get cart items
- POST/api/cart/add - Add item to cart
- POST/api/cart/remove - Remove item from cart

Orders
- POST/api/checkout - Create order from cart
- GET/api/orders?guest_id=<id> - Get order history

---

Features Implemented:

Fixed Issues
- CSS filename mismatch resolved (renamed style.css to styles.css)
- Removed duplicate code in backend
- Fixed static folder path configuration
- Implemented proper guest session management using localStorage
- Added comprehensive error handling
- Added input validation (email format, password strength)
- Improved user feedback with loading states
- Created database initialization script

Security Features
- Password hashing using Werkzeug
- Session-based authentication
- Input validation and sanitization
- SQL injection prevention (parameterized queries)

---

Usage:

1. Browse Products: Visit the home page to see available products
2. View Details: Click "View" on any product to see details
3. Add to Cart: Click "Add" or "Add to cart" to add items
4. View Cart: Navigate to Cart page to see your items
5. Checkout: Click "Checkout" to place an order
6. View Orders: Check your order history on the Orders page

---

Guest Mode:

- You can shop without creating an account
- Your cart and orders are saved using a unique guest ID stored in localStorage
- To persist data across devices, create an account

---

Development Notes:

- The backend uses Flask sessions for authenticated users
- Guest users are identified by unique IDs stored in browser localStorage
- All database operations use parameterized queries to prevent SQL injection
- Error handling has been improved throughout the application
- Loading states provide better user feedback

---

Troubleshooting:

Database Connection Issues
- Verify MySQL server is running
- Check .env file has correct credentials
- Ensure database exists (run init_database.py)

Port Already in Use
- Change the port in backend.py: app.run(debug=True, port=5001)

Styles Not Loading
- Ensure styles.css file exists (renamed from style.css)
- Check browser console for 404 errors

---

Future Enhancements:

- User profile management
- Product search and filtering
- Product reviews and ratings
- Email notifications
- Payment gateway integration
- Admin dashboard
- Product image uploads
- Advanced inventory management
