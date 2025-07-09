from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # SuperUser  
    # user = User(
    #         fname='SUPERUSER',
    #         lname='ADMIN',
    #         gender='MALE',
    #         email='superuser.admin@gmail.com',
    #         password=generate_password_hash('SUPERUSER'),
    #         contact='9876543210',
    #         address='ATUL',
    #         city='VALSAD',
    #         state='GUJARAT',
    #         role_id=1, 
    #     )
    # db.session.add(user)
    # db.session.commit()
    return render_template('home.html', title = 'Home')