
from models import User, PhoneNumber
from app import db
from flask_migrate import upgrade

upgrade()

u = User(first_name='Michael', last_name='Chen', email='michaelchensd@gmail.com', password='ch0c0l0te')
ph = PhoneNumber(number='8583753604', user=u, choices='{}', in_use=False)
db.session.add_all([u,ph])

db.session.commit()
