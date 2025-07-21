from flask import Blueprint, render_template, request
from flask_login import current_user
from app.utils.rag_chatbot import get_chatbot_response
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

class ChatbotForm(FlaskForm):
    query = TextAreaField('Query', validators=[DataRequired()])
    submit = SubmitField('Submit')

@chatbot_bp.route('/', methods=['GET', 'POST'])
def chatbot():
    form = ChatbotForm()
    response = None
    sources = []
    if form.validate_on_submit():
        query = form.query.data
        response, source_docs = get_chatbot_response(query)
        sources = [doc.page_content[:200] + "..." for doc in source_docs]
    return render_template('chatbot.html', form=form, response=response, sources=sources, title='Chat with Shopify')