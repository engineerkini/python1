import sys
import sqlite3
from datetime import datetime
from escpos.printer import Usb
import os

class ReceiptPrinter:
    def __init__(self, usb_vendor_id, usb_product_id, usb_interface):
        try:
            self.printer = Usb(usb_vendor_id, usb_product_id, usb_interface)
        except Exception as e:
            print(f"Error initializing printer: {e}")
            sys.exit(1)

    def print_receipt(self, company_name, items, total_amount, vat_rate, payment_method):
        try:
            vat_amount = total_amount * vat_rate / 100
            total_with_vat = total_amount - vat_amount

            # Print company name
            self.printer.set(align='center', width=2, height=2, text_type='B')
            self.printer.text(company_name + "\n")

            # Print date and time
            self.printer.set(align='left', width=1, height=1, text_type='A')
            self.printer.text("Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            self.printer.text("="*32 + "\n")

            # Print items
            self.printer.set(align='left', width=1, height=1, text_type='A')
            for item in items:
                self.printer.text(f"{item['name']} x{item['quantity']} @ {item['price']:.2f}\n")
                self.printer.text(f"  Subtotal: {item['quantity'] * item['price']:.2f}\n")

            # Print total amount and VAT
            self.printer.text("="*32 + "\n")
            self.printer.set(align='right', width=2, height=2, text_type='B')
            self.printer.text(f"TOTAL: {total_amount:.2f}\n")
            self.printer.text(f"VAT ({vat_rate}%): -{vat_amount:.2f}\n")
            self.printer.text(f"Total (with VAT): {total_with_vat:.2f}\n")

            # Print payment method
            self.printer.set(align='left', width=1, height=1, text_type='A')
            self.printer.text("="*32 + "\n")
            self.printer.text(f"Paid with: {payment_method}\n")

            # Print footer
            self.printer.text("="*32 + "\n")
            self.printer.set(align='center', width=1, height=1, text_type='A')
            self.printer.text("Thank you for shopping with us!\n")
            self.printer.text("\n" * 4)

            # Cut the paper
            self.printer.cut()

        except Exception as e:
            print(f"Error printing receipt: {e}")


class DatabaseHandler:
    def __init__(self, db_path='receipt_system.db'):
        self.db_path = db_path
        self.create_database_if_not_exists()

    def create_database_if_not_exists(self):
        if not os.path.exists(self.db_path):
            print(f"Database '{self.db_path}' not found. Creating database...")
            self.create_database()

    def create_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create companies table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                vat_rate REAL NOT NULL
            )
            ''')

            # Create packages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
            ''')

            # Insert sample company and packages if not exists
            cursor.execute("INSERT OR IGNORE INTO companies (name, vat_rate) VALUES ('My Store', 20.0)")
            conn.commit()

            cursor.execute("SELECT id FROM companies WHERE name = 'My Store'")
            company_id = cursor.fetchone()[0]

            # Insert sample packages for the company
            cursor.execute("INSERT OR IGNORE INTO packages (company_id, name, price, quantity) VALUES (?, 'Package 1', 10.00, 5)", (company_id,))
            cursor.execute("INSERT OR IGNORE INTO packages (company_id, name, price, quantity) VALUES (?, 'Package 2', 20.00, 3)", (company_id,))
            conn.commit()

            conn.close()
            print(f"Database '{self.db_path}' and tables created successfully.")

        except sqlite3.DatabaseError as e:
            print(f"Error creating database: {e}")
            sys.exit(1)

    def fetch_company_data(self, company_name):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, vat_rate FROM companies WHERE name = ?", (company_name,))
            company = cursor.fetchone()
            conn.close()
            return company
        except sqlite3.DatabaseError as e:
            print(f"Error fetching company data: {e}")
            return None

    def fetch_packages(self, company_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, price, quantity FROM packages WHERE company_id = ?", (company_id,))
            packages = cursor.fetchall()
            conn.close()
            return [{"name": p[0], "price": p[1], "quantity": p[2]} for p in packages]
        except sqlite3.DatabaseError as e:
            print(f"Error fetching packages: {e}")
            return []


def main():
    company_name = "My Store"  # Change to your company name
    payment_method = "Credit Card"

    # USB printer details (example values, update accordingly)
    usb_vendor_id = 0x04b8
    usb_product_id = 0x0202
    usb_interface = 0

    db_handler = DatabaseHandler()

    company = db_handler.fetch_company_data(company_name)
    if not company:
        print(f"Company {company_name} not found in database.")
        sys.exit(1)

    company_id, vat_rate = company
    items = db_handler.fetch_packages(company_id)
    total_amount = sum(item['quantity'] * item['price'] for item in items)

    printer = ReceiptPrinter(usb_vendor_id, usb_product_id, usb_interface)
    printer.print_receipt(company_name, items, total_amount, vat_rate, payment_method)


if __name__ == "__main__":
    main()
