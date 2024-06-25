import datetime
from typing import List
from extension.extension import db
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import JSON, Boolean, ForeignKey, String, Text, text, Date, exc

from faker import Faker
import pandas as pd
from extension.extension import f_bcrypt


class Role(db.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    def __repr__(self):
        return f"Role: {self.name}"


class User(db.Model):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped["Role"] = relationship(backref="user")

    def __repr__(self):
        return f"User: {self.email}"


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=text("uuid_short()")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(12), nullable=True)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    social_links: Mapped[JSON] = mapped_column(JSON, nullable=True)  # ig, email, fb
    website: Mapped[str] = mapped_column(Text, nullable=True)
    services: Mapped[JSON] = mapped_column(JSON, nullable=True)
    photos: Mapped[JSON] = mapped_column(JSON, nullable=True)

    reviews: Mapped[List["Review"]] = relationship(backref="restaurant")

    def __repr__(self):
        return f"Restaurant: {self.name}"


class Review(db.Model):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=text("uuid_short()")
    )
    review: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[str] = mapped_column(Boolean, nullable=True)  # positive, negative
    restaurant_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("restaurants.id"), nullable=False
    )
    reviewer: Mapped[User] = mapped_column(
        String(255), ForeignKey("users.email"), nullable=False
    )
    date: Mapped[Date] = mapped_column(Date, nullable=False)

    def __repr__(self):
        return f"Review created: {self.id} - {self.review}"

    # db.session.commit()


class Seeds:
    fake = Faker()
    df = pd.read_csv("C:/Users/lastg/Downloads/Dataset 2.0 - Review.csv")

    def seed(self):
        reviews = self.get_reviews()
        tracker = 0

        try:
            for _ in range(len(reviews)):
                fake_user = User(
                    email=self.fake.email(),
                    password=f_bcrypt.generate_password_hash("123"),
                    role_id=2,
                    name=self.fake.name(),
                )
                db.session.add(fake_user)
                db.session.commit()

                fake_review = Review(
                    review=reviews[tracker]["review"],
                    sentiment=reviews[tracker]["sentiment"],
                    restaurant_id=100897068469452800,
                    reviewer=fake_user.email,
                    date=self.fake.date_between(datetime.date(2022, 2, 2)),
                )

                db.session.add(fake_review)
                db.session.commit()
                tracker = tracker + 1

                print(fake_user)

        except exc.IntegrityError as ex:
            print(ex)
            db.session.rollback()

    def get_reviews(self):
        res = self.df[self.df["restaurant"] == "BO's Cafe Awok Iter"]
        res = res[["review", "sentiment"]]

        return res.to_dict("records")
