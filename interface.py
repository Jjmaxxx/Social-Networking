from neo4j_connection import Neo4jConnection
import getpass
from typing import Optional, Dict, Any, Callable, Tuple
from dataclasses import dataclass

# Context class to hold user information
@dataclass
class Context:
    user: Dict[str, Any]

# Register a new user
def Register():
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()

    if not all([name, email, username, password]):
        print("All fields are required. Registration failed.")
        return

    success = Neo4jConnection.get_instance().create_user(
        {"name": name, "email": email, "username": username, "password": password}
    )

    print(
        "Registration successful!"
        if success
        else "Someone else already has that username or email!"
    )

# Login a user
def Login() -> Context:
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    user = Neo4jConnection.get_instance().authenticate_user(username, password)

    if user is None:
        print("Invalid username or password.")
        return None

    print(f"Login successful. Welcome, {user['username']}!")
    return Context(user)

# Get user profile
def getProfile(ctx: Context):
    profile = Neo4jConnection.get_instance().get_profile(ctx.user["username"])

    if profile is None:
        print("Profile not found.")
        return

    print("\n--- Your Profile ---")
    print("Name:", profile["name"])
    print("Username:", profile["username"])
    print("Email:", profile["email"])
    print("Bio:", profile["bio"])

# Update user profile
def updateProfile(ctx: Context):
    new_name = input("New name: ")
    new_bio = input("New bio: ")
    Neo4jConnection.get_instance().update_profile(
        ctx.user["username"], new_name, new_bio
    )
    print("Profile updated.")

# Menu for guests (not logged in)
# The Tuple has two elements, the first is an optional Context storing user information 
# The second is a boolean indicating if the program should continue running
# The _ parameter means that we don't care about the value passed in
def guest_menu(_: Context) -> Tuple[Optional[Context], bool]:
    print("1. Register")
    print("2. Login")
    print("9. Exit")
    ctx = None

    # Note that match is basically the same as a switch statement in other languages
    match input("Choose an option: "):
        case "1":
            Register()
        case "2":
            ctx = Login()
        case "9":
            print("Exiting the program.")
            return None, False
        case _:
            print("Invalid option.")

    return ctx, True

# Search for a user
def searchUser(ctx: Context) -> Tuple[Optional[Context], bool]:
    search_term = input("Enter the name/username of the user you want to search for: ")
    users = Neo4jConnection.get_instance().search_users(search_term)

    if users is None:
        print("Failed to retrieve users.")
        return ctx, True

    if len(users) == 0:
        print("No users found.")
        return ctx, True

    for user in users:
        print("\n--- User Profile ---")
        print("Name:", user["name"])
        print("Username:", user["username"])
        print("Email:", user["email"])
        print("Bio:", user["bio"])

    return ctx, True


# View most popular users
def viewMostPopularUsers(ctx: Context) -> Tuple[Optional[Context], bool]:
    print("Fetching most popular users...")

    # Note that you can change the number of users to fetch by changing the number in the function call
    users = Neo4jConnection.get_instance().get_most_popular_users(3)

    if users is None:
        print("Failed to retrieve users.")
        return ctx, True

    if len(users) == 0:
        print("No users found.")
        return ctx, True

    for user in users:
        print("\n--- User Profile ---")
        print("Name:", user["name"])
        print("Username:", user["username"])
        print("Email:", user["email"])
        print("Bio:", user["bio"])
        print("Followers:", user["followers_count"])

    return ctx, True


# Menu for logged-in users
# Note that the Context is passed in as an argument to the function 
def user_menu(ctx: Context) -> Tuple[Optional[Context], bool]:
    if ctx is None:
        print("No user context found. Please log in.")
        return None, True
    print("1. View Profile")
    print("2. Edit Profile")
    print("3. Search User")
    print("4. View Most Popular Users")
    print("9. Logout")

    match input("Choose an option: "):
        case "1":
            getProfile(ctx)
        case "2":
            updateProfile(ctx)
        case "3":
            searchUser(ctx)
        case "4":
            viewMostPopularUsers(ctx)
        case "9":
            print("Logging out...")
            return None, True
        case _:
            print("Invalid option.")

    return ctx, True


# Menu dispatcher to determine which menu to show based on user context
# This function checks if ctx is present
def menu_dispatch(
    ctx: Optional[Context],
) -> Callable[[Optional[Context]], Tuple[Optional[Context], bool]]:
    if ctx is None:
        return guest_menu

    return user_menu

# Standard practice in python to check if the script is being run directly
if __name__ == "__main__":
    ctx: Optional[Context] = None

    while f := menu_dispatch(ctx):
        # Clear the console (this is a simple way to clear the console)
        # The string "\033[H\033[J" is an ANSI escape code that clears the screen
        print("\033[H\033[J", end="")

        ctx, continue_program = f(ctx)
        if not continue_program:
            break

        input("Press Enter to continue...")
