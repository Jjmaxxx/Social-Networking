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


def guest_menu(ctx: Optional[Context]) -> Tuple[Optional[Context], bool]:
    print("1. Register")
    print("2. Login")
    print("3. Exit")

    match input("Choose an option: "):
        case "1":
            Register()
        case "2":
            ctx = Login()
        case "3":
            print("Exiting the program.")
            return None, False
        case _:
            print("Invalid option.")

    return ctx, True


def user_menu(ctx: Context) -> Tuple[Optional[Context], bool]:
    print("1. View Profile")
    print("2. Edit Profile")
    print("3. Logout")

    match input("Choose an option: "):
        case "1":
            getProfile(ctx)
        case "2":
            updateProfile(ctx)
        case "3":
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

        input('Press Enter to continue...')
