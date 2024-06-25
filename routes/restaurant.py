from flask import Blueprint, json, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from model.model import Restaurant, Review, db
from model.schema import RestaurantSchema, ReviewSchema
from utils.lr_model import LR_Model


bp = Blueprint("restaurant", __name__)
one_restaurant = RestaurantSchema()
many_restaurant = RestaurantSchema(many=True)
many_review = ReviewSchema(many=True)


def predict_sentiment():
    reviews = Review.query.filter_by(sentiment=None).all()

    return many_review.dump(reviews)


def get_reviews_count(restaurant_id):
    no_review = (
        db.session.query(func.count(Review.id).label("reviews"))
        .filter_by(restaurant_id=restaurant_id)
        .first()
    )
    positive_review = (
        db.session.query(func.count(Review.id).label("reviews"))
        .filter_by(restaurant_id=restaurant_id, sentiment=True)
        .first()
    )

    return {
        "no_review": no_review.reviews,
        "positive_review": positive_review.reviews,
    }


def get_restaurants_summary(query):
    restaurants = []

    for item in query:
        review_summary = get_reviews_count(item.id)

        restaurants.append(
            {
                "id": item.id,
                "name": item.name,
                "photos": item.photos,
                "category": item.category,
                "services": item.services,
                "no_review": review_summary["no_review"],
                "positive_review": review_summary["positive_review"],
            }
        )

    return restaurants


@bp.get("/restaurant")
def get_all_restaurants():
    restaurant = Restaurant.query.all()
    restaurants = get_restaurants_summary(query=restaurant)

    if not restaurant:
        return jsonify(message="Could not find any restaurant")

    return jsonify(restaurant=restaurants)


@bp.get("/restaurant/search")
def get_restaurant_by_query():
    query = request.args
    category = query.get("category")
    sentiment = query.get("sentiment")
    name = query.get("name")
    location = query.get("location")
    other = query.get("other")

    restaurant = (
        db.session.query(Restaurant).join(Restaurant.reviews).group_by(Restaurant.id)
    )

    if sentiment is not None and sentiment:
        lr_model = LR_Model()
        predict_res = lr_model.predict(sentiment)
        print(predict_res)

        restaurant = restaurant.filter_by(sentiment=predict_res)

    if category is not None and category:
        restaurant = restaurant.filter_by(Restaurant.category.contains(category))

    if name is not None and name:
        restaurant = restaurant.filter_by(Restaurant.name.contains(name))

    if location is not None and location:
        restaurant = restaurant.filter_by(Restaurant.location.contains(location))

    if other is not None and other == "most_review":
        restaurant = restaurant.order_by(func.count(Review.id).desc())

    restaurant = restaurant.all()
    restaurants = get_restaurants_summary(query=restaurant)

    if not restaurant:
        return jsonify(message="Could not find any restaurant")

    return jsonify(restaurant=restaurants)


@bp.get("/restaurant/statistics")
def get_restaurant_():
    restaurant = (
        db.session.query(
            Restaurant.id,
            Restaurant.name,
            Restaurant.category,
            func.count(Review.id).label("no_reviews"),
        )
        .join(Restaurant.reviews)
        .group_by(Restaurant.id)
        .all()
    )

    statistics_json = []
    for item in restaurant:
        statistics_json.append(
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "no_reviews": item.no_reviews,
            }
        )

    if not restaurant:
        return jsonify(message="Could not find any restaurant"), 404

    return jsonify(restaurant=statistics_json)


@bp.get("/restaurant/<id>")
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    restaurant_details = one_restaurant.dump(restaurant)
    review_summary = get_reviews_count(id)

    reviews = []
    for review in restaurant.reviews:
        reviews.append(
            {
                "id": review.id,
                "review": review.review,
                "sentiment": review.sentiment,
                "reviewer": review.reviewer,
                "date": review.date,
            }
        )

    restaurant_details["reviews"] = reviews
    restaurant_details["no_review"] = review_summary["no_review"]
    restaurant_details["positive_review"] = review_summary["positive_review"]

    if not restaurant:
        return jsonify(message="Could not find any restaurant"), 404

    return jsonify(restaurant=restaurant_details)


@bp.post("/restaurant")
@jwt_required()
def add_restaurant():
    data = json.loads(request.data)
    services = " · ".join(data["services"])
    photos = {
        "profile": {
            "link": data["profile_link"],
        },
        "bg": {
            "link": data["bg_link"],
        },
    }
    links = {
        "email": data["email"],
        "fb": data["fb"],
        "ig": data["ig"],
    }

    restaurant = Restaurant(
        name=data["name"],
        description=data["description"],
        category=data["category"],
        phone=data["phone"],
        location=data["location"],
        social_links=links,
        website=data["website"],
        services=services,
        photos=photos,
    )

    db.session.add(restaurant)
    db.session.commit()

    return jsonify(message="Restaurant registered successfully"), 201


@bp.put("/restaurant/<id>")
@jwt_required()
def update_restaurant(id):
    data = json.loads(request.data)
    restaurant = Restaurant.query.filter_by(id=id).first()
    services = " · ".join(data["services"])
    photos = {
        "profile": {
            "link": data["profile_link"],
        },
        "bg": {
            "link": data["bg_link"],
        },
    }
    links = {
        "email": data["email"],
        "fb": data["fb"],
        "ig": data["ig"],
    }

    if not restaurant:
        return jsonify(message="Could not find any restaurant"), 404

    restaurant.name = data["name"]
    restaurant.description = data["description"]
    restaurant.category = data["category"]
    restaurant.phone = data["phone"]
    restaurant.location = data["location"]
    restaurant.social_links = links
    restaurant.website = data["website"]
    restaurant.services = services
    restaurant.photos = photos

    db.session.commit()

    return jsonify(message="Restaurant updated successfully")
