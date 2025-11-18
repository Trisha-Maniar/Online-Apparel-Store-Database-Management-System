"""
Database Initialization Script
Creates all required tables for the Online Apparel Store DBMS project.
Run this script once to set up your database schema.
"""

import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', ''),
    'database': os.getenv('DB_NAME', 'online_apparel_store_dbms'),
    'cursorclass': pymysql.cursors.DictCursor
}

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    config = DB_CONFIG.copy()
    db_name = config.pop('database')
    
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"✓ Database '{db_name}' ready")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        raise

def init_tables():
    """Initialize all database tables"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Creating tables...")
        
        # Users table (already created by backend, but included for completeness)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            customer_id INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """)
        print("✓ users table")
        
        # Product table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product (
            Product_ID INT AUTO_INCREMENT PRIMARY KEY,
            Product_Name VARCHAR(255) NOT NULL,
            Description TEXT,
            Price DECIMAL(10, 2) NOT NULL,
            Discount DECIMAL(5, 2) DEFAULT 0,
            Brand VARCHAR(100),
            Category VARCHAR(100),
            Size VARCHAR(50),
            Color VARCHAR(50),
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """)
        print("✓ product table")
        
        # Inventory table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            Product_ID INT PRIMARY KEY,
            Quantity_Available INT NOT NULL DEFAULT 0,
            Reorder_Level INT DEFAULT 10,
            Last_Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (Product_ID) REFERENCES product(Product_ID) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """)
        print("✓ inventory table")
        
        # Cart table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            Customer_ID INT NOT NULL,
            Product_ID INT NOT NULL,
            Quantity INT NOT NULL DEFAULT 1,
            Added_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (Customer_ID, Product_ID),
            FOREIGN KEY (Product_ID) REFERENCES product(Product_ID) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """)
        print("✓ cart table")
        
        # Orders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            Order_ID INT AUTO_INCREMENT PRIMARY KEY,
            Customer_ID INT NOT NULL,
            Order_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Total_Amount DECIMAL(10, 2) NOT NULL,
            Payment_Method VARCHAR(50),
            Payment_Status VARCHAR(50) DEFAULT 'Pending',
            Order_Status VARCHAR(50) DEFAULT 'Processing',
            Shipping_Address TEXT,
            Delivery_Date DATE NULL
        ) ENGINE=InnoDB;
        """)
        print("✓ orders table")
        
        # Order Items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_item (
            Order_Item_ID INT AUTO_INCREMENT PRIMARY KEY,
            Order_ID INT NOT NULL,
            Product_ID INT NOT NULL,
            Quantity INT NOT NULL,
            Price_at_Purchase DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (Order_ID) REFERENCES orders(Order_ID) ON DELETE CASCADE,
            FOREIGN KEY (Product_ID) REFERENCES product(Product_ID) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """)
        print("✓ order_item table")
        
        # Payment table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment (
            Payment_ID INT AUTO_INCREMENT PRIMARY KEY,
            Order_ID INT NOT NULL,
            Payment_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Payment_Method VARCHAR(50) NOT NULL,
            Amount_Paid DECIMAL(10, 2) NOT NULL,
            Transaction_ID VARCHAR(100),
            Payment_Status VARCHAR(50) DEFAULT 'Pending',
            FOREIGN KEY (Order_ID) REFERENCES orders(Order_ID) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """)
        print("✓ payment table")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ All tables created successfully!")
        print("\nYou can now run the Flask backend server.")
        
    except pymysql.Error as e:
        print(f"✗ Database error: {e}")
        raise
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

def insert_sample_data():
    """Insert sample products for testing (optional)"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if products already exist
        cursor.execute("SELECT COUNT(*) FROM product")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"\nSample data already exists ({count} products). Skipping...")
            cursor.close()
            conn.close()
            return
        
        print("\nInserting sample products...")
        
        sample_products = [
            ("Cotton T-Shirt", "Comfortable cotton t-shirt for everyday wear", 599.00, 10, "BasicWear", "Tops", "M", "Blue"),
            ("Denim Jeans", "Classic fit denim jeans", 1299.00, 15, "DenimCo", "Bottoms", "32", "Blue"),
            ("Running Shoes", "Lightweight running shoes with cushioned sole", 2499.00, 20, "SportMax", "Footwear", "9", "Black"),
            ("Hooded Sweatshirt", "Warm and cozy hooded sweatshirt", 899.00, 5, "ComfortZone", "Tops", "L", "Gray"),
            ("Formal Shirt", "Professional formal shirt for office wear", 799.00, 0, "FormalWear", "Tops", "M", "White"),
        ]
        
        for product in sample_products:
            cursor.execute("""
                INSERT INTO product (Product_Name, Description, Price, Discount, Brand, Category, Size, Color)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, product)
            
            # Get the inserted product ID and add inventory
            product_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO inventory (Product_ID, Quantity_Available, Reorder_Level)
                VALUES (%s, %s, %s)
            """, (product_id, 50, 10))
        
        conn.commit()
        print(f"✓ Inserted {len(sample_products)} sample products with inventory")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error inserting sample data: {e}")

if __name__ == '__main__':
    print("=" * 50)
    print("Online Apparel Store - Database Initialization")
    print("=" * 50)
    print()
    
    try:
        create_database_if_not_exists()
        init_tables()
        
        # Ask if user wants sample data
        response = input("\nInsert sample products? (y/n): ").strip().lower()
        if response == 'y':
            insert_sample_data()
        
        print("\n" + "=" * 50)
        print("Database setup complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nPlease check your database configuration in .env file")

