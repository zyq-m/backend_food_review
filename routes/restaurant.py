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


@bp.get("/restaurant")
def get_all_restaurants():
    restaurant = Restaurant.query.all()

    if not restaurant:
        return jsonify(message="Could not find any restaurant")

    return jsonify(restaurant=many_restaurant.dump(restaurant))


@bp.get("/restaurant/search")
def get_restaurant_by_query():
    query = request.args
    category = query.get("category")
    name = query.get("name")
    sentiment = query.get("sentiment")
    location = query.get("location")
    other = query.get("other")

    restaurant = (
        db.session.query(Restaurant).join(Restaurant.reviews).group_by(Restaurant.id)
    )

    if category is not None and category:
        restaurant = restaurant.filter_by(Restaurant.category.contains(category))

    if name is not None and name:
        restaurant = restaurant.filter_by(Restaurant.name.contains(name))

    if location is not None and location:
        restaurant = restaurant.filter_by(Restaurant.location.contains(location))

    if other is not None and other == "most_review":
        restaurant = restaurant.order_by(func.count(Review.id).desc())

    if sentiment is not None and sentiment:
        lr_model = LR_Model()
        predict_res = lr_model.predict(sentiment)

        print(predict_res)

    restaurant = restaurant.all()

    if not restaurant:
        return jsonify(message="Could not find any restaurant")

    return jsonify(restaurant=many_restaurant.dump(restaurant))


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
            "profile_img": data["profile_img"],
            "profile_link": data["profile_link"],
        },
        "bg": {
            "bg_img": data["bg_img"],
            "bg_link": data["bg_link"],
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

    if not restaurant:
        return jsonify(message="Could not find any restaurant"), 404

    restaurant.name = data["name"]
    restaurant.description = data["description"]
    restaurant.category = data["category"]
    restaurant.phone = data["phone"]
    restaurant.location = data["location"]
    restaurant.social_links = data["social_links"]
    restaurant.website = data["website"]
    restaurant.service = data["service"]

    db.session.commit()

    return jsonify(message="Restaurant updated successfully")
