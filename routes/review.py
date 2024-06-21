from flask import Blueprint, jsonify, request

from model.model import Review
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

    if not query:
        reviews = Review.query.filter_by(restaurant_id=id).all()

        return filter_review_response(reviews)

    if sentiment and date is not None:
        reviews = (
            Review.query.filter_by(restaurant_id=id, sentiment=sentiment)
            .order_by(
                Review.date.desc() if date == "desc" else Review.date.asc(),
            )
            .all()
        )

        return filter_review_response(reviews)

    if date is not None:
        reviews = (
            Review.query.filter_by(restaurant_id=id)
            .order_by(
                Review.date.desc() if date == "desc" else Review.date.asc(),
            )
            .all()
        )

        return filter_review_response(reviews)

    if sentiment is not None:
        reviews = Review.query.filter_by(restaurant_id=id, sentiment=sentiment).all()

        return filter_review_response(reviews)
