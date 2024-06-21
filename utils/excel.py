import pandas as pd
from extension.extension import db
from model.model import Restaurant, Review

res_df = pd.read_excel(
    "Dataset 2.0.xlsx",
    sheet_name="Restaurant",
    usecols=[
        "restaurant_name",
        "intro",
        "category",
        "location",
        "phone",
        "services",
        "email",
        "fb",
        "website",
    ],
)
rev_df = pd.read_excel(
    "Dataset 2.0.xlsx",
    sheet_name="Review",
    usecols=["restaurant", "reviewer", "date", "review"],
)

#  Clean the “Phone_Number” column by removing non-alphanumeric characters
res_df["phone"] = res_df["phone"].str.replace(r"[^0-9]+", "", regex=True)

new_res_df = res_df.fillna(value="null")

# Convert the cleaned phone numbers to strings (optional, but recommended)
new_res_df["phone"] = new_res_df["phone"].apply(lambda x: str(x))

res_dict = new_res_df.to_dict("records")
rev_dict = rev_df.to_dict("records")


def add_restaurant_review():
    for res_item in res_dict:
        social_links = [{"fb": res_item["fb"]}]
        if res_item["email"] != "null":
            social_links.append({"email": res_item["email"]})

        website = None
        if res_item["website"] != "null":
            website = res_item["website"]

        phone = None
        if res_item["phone"] != "null":
            phone = res_item["phone"]

        restaurant = Restaurant(
            name=res_item["restaurant_name"],
            description=res_item["intro"],
            category=res_item["category"],
            phone=phone,
            location=res_item["location"],
            social_links=social_links,
            website=website,
            services=res_item["services"],
        )

        db.session.add(restaurant)

        for rev_item in rev_dict:
            if res_item["restaurant_name"] == rev_item["restaurant"]:
                review = Review(
                    review=rev_item["review"],
                    restaurant=restaurant,
                    reviewer=rev_item["reviewer"],
                    date=rev_item["date"],
                )

                db.session.add(review)

        db.session.commit()
