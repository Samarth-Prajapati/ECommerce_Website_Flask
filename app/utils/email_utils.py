from flask_mail import Message
from flask import current_app
from app import mail  
import os

def send_invoice_email(to_email, invoice):
    msg = Message(
        subject=f"Your Invoice #{invoice.id}",
        recipients=[to_email], 
        body=f"""Hi,

Thank you for your purchase! Please find attached your invoice #{invoice.id}.

Regards,
E-Commerce Team"""
    )
    pdf_path = os.path.join(current_app.root_path, 'static', invoice.pdf_path)
    with open(pdf_path, 'rb') as f:
        msg.attach(
            filename=f"Invoice_{invoice.id}.pdf",         
            content_type='application/pdf',               
            data=f.read()                                 
        )
    mail.send(msg)
