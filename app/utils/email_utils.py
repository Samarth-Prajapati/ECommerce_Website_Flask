from flask_mail import Message
from flask import current_app
from app import mail  
import os

def send_invoice_email(to_email, invoice):
    msg = Message(
        subject=f"Your Invoice for Order #{invoice.order_id}",
        recipients=[to_email], 
        body=f"""Hi,

Thank you for your purchase! Please find attached your invoice below.

Regards,
E-Commerce Team"""
    )
    pdf_path = os.path.join(current_app.root_path, 'static', invoice.pdf_path)
    with open(pdf_path, 'rb') as f:
        msg.attach(
            filename=f"Invoice.pdf",         
            content_type='application/pdf',               
            data=f.read()                                 
        )
    mail.send(msg)

def send_report_email(recipient_email, subject, body, attachment_path):
    msg = Message(subject, recipients=[recipient_email])
    msg.body = body
    with open(attachment_path, 'rb') as f:
        filename = os.path.basename(attachment_path)
        msg.attach(filename, "text/csv", f.read())
    mail.send(msg)
