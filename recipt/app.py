from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

def calculate_vat(amount):
    vat_rate = 0.16  # 16% VAT rate
    return amount * vat_rate

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    date = request.form['date']
    description = request.form['description']
    amount = float(request.form['amount'])
    vat = calculate_vat(amount)

    conn = sqlite3.connect('kra_returns.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transactions (date, description, amount, vat)
    VALUES (?, ?, ?, ?)
    ''', (date, description, amount, vat))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/generate_form')
def generate_form():
    conn = sqlite3.connect('kra_returns.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions')
    transactions = cursor.fetchall()
    conn.close()

    file_name = 'kra_returns_form.pdf'
    pdf = canvas.Canvas(file_name, pagesize=A4)
    pdf.setTitle('KRA Returns Form')

    pdf.drawString(100, 800, 'KRA Returns Form')
    pdf.drawString(100, 780, 'Date: ' + datetime.now().strftime('%Y-%m-%d'))

    y = 750
    pdf.drawString(100, y, 'ID')
    pdf.drawString(150, y, 'Date')
    pdf.drawString(250, y, 'Description')
    pdf.drawString(450, y, 'Amount')
    pdf.drawString(550, y, 'VAT')

    for transaction in transactions:
        y -= 20
        pdf.drawString(100, y, str(transaction[0]))
        pdf.drawString(150, y, transaction[1])
        pdf.drawString(250, y, transaction[2])
        pdf.drawString(450, y, "{:.2f}".format(transaction[3]))
        pdf.drawString(550, y, "{:.2f}".format(transaction[4]))

    pdf.save()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)