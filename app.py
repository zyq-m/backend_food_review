from datetime import timedelta
from flask import Flask
from extension import extension
from routes import auth, restaurant, review

app = Flask(__name__)

# configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@localhost/food_directory"
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

# extensions
extension.db.init_app(app)
extension.ma.init_app(app)
extension.jwt.init_app(app)
extension.cors.init_app(app)
extension.f_bcrypt.init_app(app)

# register route
app.register_blueprint(auth.bp)
app.register_blueprint(restaurant.bp)
app.register_blueprint(review.bp)
