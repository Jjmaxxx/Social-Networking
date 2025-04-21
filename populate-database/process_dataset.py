import pandas as pd
from faker import Faker
import random

# load dataset
df = pd.read_csv('SocialMediaUsersDataset.csv')

# drop unnecessary columns
drop_cols = ['Gender', 'Interests']
df = df.drop(columns=drop_cols)

# truncate dataset to 1,000 rows
df = df.sample(n=1000, random_state=42)

# add new columns with fake data
fake = Faker()
# Generate unique usernames
unique_usernames = set()
while len(unique_usernames) < len(df):
    unique_usernames.add(fake.user_name())
df['Username'] = list(unique_usernames)
df['Password'] = [fake.password() for _ in range(len(df))]
df['Email'] = [fake.email() for _ in range(len(df))]
df['Bio'] = [fake.sentence(nb_words=10) for _ in range(len(df))]

# save to csv
csv_path = 'processed_dataset.csv'
df.to_csv(csv_path, index=False)