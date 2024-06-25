from datetime import date
from email import message
from flask import Blueprint, json, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import exc

from model.model import Review, db
from model.schema import ReviewSchema


bp = Blueprint("review", __name__)
many_review = ReviewSchema(many=True)


def filter_review_response(reviews):
    reviews_detail = many_review.dump(reviews)

    if not reviews:
        return jsonify(message="Reviews not found")

    return jsonify(reviews=reviews_detail)


@bp.get("/review/restaurant/<id>/sort")
def get_reviews(id):
    query = request.args
    sentiment = query.get("sentiment")
    date = query.get("date")

    reviews = Review.query.filter_by(restaurant_id=id)

    if sentiment is not None and sentiment:
        reviews = reviews.filter_by(sentiment=sentiment)

    if date is not None and date:
        reviews = reviews.filter_by(restaurant_id=id, sentiment=sentiment).order_by(
            Review.date.desc() if date == "desc" else Review.date.asc(),
        )

    reviews = reviews.all()
    reviews_detail = many_review.dump(reviews)

    return jsonify(reviews=reviews_detail)


@bp.post("/review")
@jwt_required()
def add_review():
    data = json.loads(request.data)
    user = get_jwt_identity()

    if user["role"]["role"] == "admin":
        return jsonify(message="You are not allowed"), 400

    check_review = Review.query.filter_by(
        restaurant_id=data["restaurant_id"], reviewer=user["email"]
    ).first()

    if check_review:
        return jsonify(message="You only can review once per restaurant"), 400

    review = Review(
        restaurant_id=data["restaurant_id"],
        review=data["review"],
        reviewer=user["email"],
        sentiment=data["sentiment"],
        date=date.today(),
    )

    db.session.add(review)
    db.session.commit()

    return jsonify(message="Review posted successfully"), 201
