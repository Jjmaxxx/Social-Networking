import pandas as pd
import random

# load Users
users_df = pd.read_csv("processed_dataset.csv")
usernames = users_df["Username"].tolist()

# set a fixed random seed for reproducibility
random.seed(42)

# create FOLLOW relationships
relationships = []
for user in usernames:
    follows = random.sample([u for u in usernames if u != user], 25)  # Each user follows 25 others
    for follow in follows:
        relationships.append({"Follower": user, "Followed": follow})

# Save to CSV
relationships_df = pd.DataFrame(relationships)
relationships_df.to_csv("follows.csv", index=False)