from neo4j_connection import Neo4jConnection
import getpass
from typing import Optional, Dict, Any, Callable, Tuple
from dataclasses import dataclass


@dataclass
class Context:
    user: Dict[str, Any]


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


def Login() -> Context:
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    user = Neo4jConnection.get_instance().authenticate_user(username, password)

    if user is None:
        print("Invalid username or password.")
        return None

    print(f"Login successful. Welcome, {user['username']}!")
    return Context(user)


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


def updateProfile(ctx: Context):
    new_name = input("New name: ")
    new_bio = input("New bio: ")
    Neo4jConnection.get_instance().update_profile(
        ctx.user["username"], new_name, new_bio
    )
    print("Profile updated.")


def guest_menu(_: Context) -> Tuple[Optional[Context], bool]:
    print("1. Register")
    print("2. Login")
    print("9. Exit")
    ctx = None

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


def viewMostPopularUsers(ctx: Context) -> Tuple[Optional[Context], bool]:
    print("Fetching most popular users...")
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


def user_menu(ctx: Context) -> Tuple[Optional[Context], bool]:
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


def menu_dispatch(
    ctx: Optional[Context],
) -> Callable[[Optional[Context]], Tuple[Optional[Context], bool]]:
    if ctx is None:
        return guest_menu

    return user_menu


if __name__ == "__main__":
    ctx: Optional[Context] = None

    while f := menu_dispatch(ctx):
        print("\033[H\033[J", end="")

        ctx, continue_program = f(ctx)
        if not continue_program:
            break

        input("Press Enter to continue...")
