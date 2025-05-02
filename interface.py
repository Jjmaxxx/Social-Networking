from neo4j_connection import Neo4jConnection
import getpass
import os

conn = Neo4jConnection()

class ContextManager():
    def __init__(self, user):
        self.user = user

def Register():
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    if not all([name, email, username, password]):
        print("All fields are required. Registration failed.")
    else:
        success = conn.create_user({
            "name": name,
            "email": email,
            "username": username,
            "password": password
        })
        print("Registration successful!" if success else "Someone else already has that username or email!")

def Login() -> ContextManager:
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    user = conn.authenticate_user(username, password)
    if user:
        print(f"Login successful. Welcome, {user['username']}!")
        return ContextManager(user)
    else:
        print("Invalid credentials.")

def getProfile(user:ContextManager):
    if not user:
        print("You need to be logged in to view your profile.")
        return
    profile = conn.get_profile(user['username'])
    if profile:
        print("\n--- Your Profile ---")
        print("Name:", profile["name"])
        print("Username:", profile["username"])
        print("Email:", profile["email"])
        print("Bio:", profile["bio"])
    else:
        print("Profile not found.")

# def updateProfile():  
#     if current_user:
#         new_name = input("New name: ")
#         new_bio = input("New bio: ")
#         conn.update_profile(current_user['username'], new_name, new_bio)
#         print("Profile updated.")
#     else:
#         print("You need to be logged in to update your profile.")

# def Logout():
#     current_user = None
#     current_username = None
#     print("Logged out.")


ctx = ContextManager(None)
while True:

    if not ctx.user:
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")
        # os.system("clear")
        match choice:
            case "1":
                Register()
            case "2":
                f = Login()
            case "3":
                print("Exiting the program.")
                break
            case _:
                print("Invalid option.")

    else:
        print("\n--- Logged in as:", ctx.user['username'], "---")
        print("1. View Profile")
        print("2. Edit Profile")
        print("3. Logout")
        choice = input("Choose an option: ")
        # os.system("clear")
        match choice:
            case "1":
                getProfile()
            # case "2":
            #     updateProfile()
            # case "3":
            #     Logout()
            case _:
                print("Invalid option.")
conn.close()