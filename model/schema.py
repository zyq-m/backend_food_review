from extension.extension import ma
from model.model import Restaurant, Review, Role, User


class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("email", "role")

    role = ma.auto_field()


class RestaurantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Restaurant


class ReviewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Review

    reviewer = ma.auto_field()
