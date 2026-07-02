import pandas as pd
from database import engine

def build_tables():

    df = pd.read_sql("SELECT * FROM airbnb_raw", engine)

    # HOSTS TABLE
    hosts = df[['Host ID','Host Name','Host URL','Host Since']].drop_duplicates()
    hosts.to_sql("hosts", engine, if_exists="replace", index=False)

    # LISTINGS TABLE
    listings = df[['Listing ID','Listing Name','Price','Property Type']].drop_duplicates()
    listings.to_sql("listings", engine, if_exists="replace", index=False)

    # REVIEWS TABLE
    reviews = df[['Review ID','Listing ID','Comments','review_date']].drop_duplicates()
    reviews.to_sql("reviews", engine, if_exists="replace", index=False)

    # RATINGS TABLE
    ratings = df[['Listing ID','Overall Rating','Accuracy Rating']].drop_duplicates()
    ratings.to_sql("ratings", engine, if_exists="replace", index=False)

    print("Tables created successfully!")

if __name__ == "__main__":
    build_tables()