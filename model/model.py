from typing import List
from extension.extension import db
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import JSON, ForeignKey, String, Text, text, Date


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
    hours: Mapped[str] = mapped_column(Text, nullable=True)
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
    sentiment: Mapped[str] = mapped_column(
        String(10), nullable=True
    )  # positive, negative, neutral
    restaurant_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("restaurants.id"), nullable=False
    )
    reviewer: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)

    def __repr__(self):
        return f"Review created: {self.id} - {self.review}"
