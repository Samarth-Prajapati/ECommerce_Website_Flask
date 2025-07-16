import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import current_app
from app import db  

def generate_invoice_pdf(invoice):
    filename = f"invoice_{invoice.id}.pdf"
    folder = os.path.join(current_app.root_path, "static", "invoices")
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(220, height - 50, "INVOICE")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Invoice ID: {invoice.id}")
    # c.drawString(50, height - 120, f"Order ID: {invoice.order_id}")
    c.drawString(50, height - 160, f"Date: {invoice.created_at.strftime('%Y-%m-%d')}")

    y = height - 200
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Amount before Tax:")
    c.drawString(300, y, f"₹ {invoice.total_before_tax:.2f}")
    y -= 20
    c.drawString(50, y, f"GST ({invoice.gst_percent}%):")
    c.drawString(300, y, f"₹ {invoice.total_gst:.2f}")
    y -= 20
    c.drawString(50, y, "Total Amount Paid:")
    c.drawString(300, y, f"₹ {invoice.total_after_tax:.2f}")

    y -= 40
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, "Thank you for shopping with us!")

    c.save()

    relative_path = os.path.relpath(filepath, os.path.join(current_app.root_path, 'static'))
    invoice.pdf_path = relative_path.replace("\\", "/") 
    db.session.commit()

