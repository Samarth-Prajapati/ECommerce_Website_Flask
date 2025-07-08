from werkzeug.security import generate_password_hash, check_password_hash

def set_hashPassword(passwordDefault):
    return generate_password_hash(passwordDefault)

def check_password(passwordDefault, password):
    return check_password_hash(passwordDefault, password)