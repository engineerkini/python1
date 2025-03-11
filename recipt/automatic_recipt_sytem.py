import sys
import sqlite3
from datetime import datetime
from escpos.printer import Usb

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

def fetch_company_data(company_name):
    conn = sqlite3.connect('receipt_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, vat_rate FROM companies WHERE name = ?", (company_name,))
    company = cursor.fetchone()
    conn.close()
    return company

def fetch_packages(company_id):
    conn = sqlite3.connect('receipt_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, quantity FROM packages WHERE company_id = ?", (company_id,))
    packages = cursor.fetchall()
    conn.close()
    return [{"name": p[0], "price": p[1], "quantity": p[2]} for p in packages]

if __name__ == "__main__":
    company_name = "My Store"  # Change to your company name
    payment_method = "Credit Card"

    # USB printer details (example values, update accordingly)
    usb_vendor_id = 0x04b8
    usb_product_id = 0x0202
    usb_interface = 0

    company = fetch_company_data(company_name)
    if not company:
        print(f"Company {company_name} not found in database.")
        sys.exit(1)

    company_id, vat_rate = company
    items = fetch_packages(company_id)
    total_amount = sum(item['quantity'] * item['price'] for item in items)

    printer = ReceiptPrinter(usb_vendor_id, usb_product_id, usb_interface)
    printer.print_receipt(company_name, items, total_amount, vat_rate, payment_method)