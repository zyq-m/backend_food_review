from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


cors = CORS()
jwt = JWTManager()
ma = Marshmallow()
db = SQLAlchemy(model_class=Base)
f_bcrypt = Bcrypt()

f_bcrypt.generate_password_hash("admin123").decode("utf-8")
