import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import current_app
from app import db  
from app.models import Invoice, Order, Product, User
from reportlab.lib import colors

def generate_invoice_pdf(invoice):
    filename = f"invoice_{invoice.id}.pdf"
    folder = os.path.join(current_app.root_path, "static", "invoices")
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    title_x = 40
    title_y = height - 50

    c.setFont("Times-Italic", 48)  
    c.setFillColorRGB(0.1, 0.3, 0.5)
    c.drawString(title_x, title_y, "S")

    c.setFont("Helvetica-Oblique", 24)
    c.drawString(title_x + 23, title_y + 1, "hopify Invoice")

    c.setFont("Helvetica", 12)

    order = Order.query.get(invoice.order_id)
    user = User.query.get(order.user_id)
    c.drawString(400, height - 120, f"Order ID: {invoice.order_id}")
    c.drawString(400, height - 140, f"Date: {invoice.created_at.strftime('%Y-%m-%d')}")

    c.drawString(50, height - 100, f"Bill To:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 120, f"{user.fname} {user.lname}")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 140, f"Email: {user.email}")

    y = height - 180
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Amount before Tax:")
    c.drawString(250, y, f"$ {invoice.total_before_tax:.2f}")
    y -= 20
    c.drawString(50, y, f"GST ({invoice.gst_percent}%):")
    c.drawString(250, y, f"$ {invoice.total_gst:.2f}")
    y -= 20
    c.drawString(50, y, "Total Amount Paid:")
    c.drawString(250, y, f"$ {invoice.total_after_tax:.2f}")

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.grey)
    c.rect(50, y, 500, 25, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.drawString(55, y + 7, "Product")
    c.drawString(240, y + 7, "Quantity")
    c.drawString(320, y + 7, "Unit Price")
    c.drawString(420, y + 7, "Total")

    y -= 25
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)

    for item in order.order_items:
        product = Product.query.get(item.product_id)
        if y < 100:
            c.showPage()
            y = height - 80  
        c.rect(50, y, 500, 25, fill=False, stroke=True)
        c.drawString(55, y + 7, product.name)
        c.drawString(245, y + 7, str(item.quantity))
        c.drawString(325, y + 7, f"$ {item.price:.2f}")
        c.drawString(425, y + 7, f"$ {item.price * item.quantity:.2f}")
        y -= 25

    y -= 30
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, "Thank you for shopping with Shopify!")

    c.save()

    relative_path = os.path.relpath(filepath, os.path.join(current_app.root_path, 'static'))
    invoice.pdf_path = relative_path.replace("\\", "/") 
    db.session.commit()
    return invoice.pdf_path

