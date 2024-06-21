from email import message
from flask import Blueprint, json, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import exc
from extension.extension import f_bcrypt
from model.model import User, db
from model.schema import UserSchema

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    data = json.loads(request.data)
    user = User.query.filter_by(email=data["email"]).first()
    single_user = UserSchema()

    if not user:
        return jsonify(message="User not found"), 404

    if not f_bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify(message="Password incorrect"), 400

    user_details = single_user.dump(user)
    user_details["role"] = {"id": user.role.id, "role": user.role.name}

    access_token = create_access_token(user_details)
    refresh_token = create_refresh_token(user_details)

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@bp.post("/sign_up")
def sign_up():
    data = json.loads(request.data)

    if (
        data["email"] == ""
        or data["password"] == ""
        or data["con_password"] == ""
        or data["first_name"] == ""
    ):
        return jsonify(message="Please enter invalid credentials"), 400

    if data["password"] != data["con_password"]:
        return jsonify(message="Confirm password incorrect"), 400

    try:
        name = (
            f'{data["first_name"]} {data["last_name"]}'
            if data["last_name"]
            else data["first_name"]
        )
        new_user = User(
            email=data["email"],
            name=name,
            password=f_bcrypt.generate_password_hash(data["password"]),
            role_id=2,
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify(message="Signup successful. Please log in to your account"), 201
    except exc.IntegrityError as ex:
        print(ex)
        return jsonify(message="Email already in use"), 400


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
