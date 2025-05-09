from neo4j_connection import Neo4jConnection
import getpass
from typing import Optional, Dict, Any, Callable, Tuple
from dataclasses import dataclass

# Context class to hold user information
@dataclass
class Context:
    user: Dict[str, Any]

# Register a new user (UC-1)
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

# Login a user (UC-2)
def Login() -> Context:
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    user = Neo4jConnection.get_instance().authenticate_user(username, password)

    if user is None:
        print("Invalid username or password.")
        return None

    print(f"Login successful. Welcome, {user['username']}!")
    return Context(user)

# Get user profile (UC-3)
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

# Update user profile (UC-4)
def updateProfile(ctx: Context):
    new_name = input("New name: ")
    new_bio = input("New bio: ")
    Neo4jConnection.get_instance().update_profile(
        ctx.user["username"], new_name, new_bio
    )
    print("Profile updated.")

# Follow another user (UC-5)
def followUser(ctx: Context) -> Tuple[Optional[Context], bool]:
    username_to_follow = input("Enter username to follow: ")
    
    # Don't allow following yourself
    if username_to_follow == ctx.user["username"]:
        print("You cannot follow yourself.")
        return ctx, True
    
    success = Neo4jConnection.get_instance().follow_user(
        ctx.user["username"], username_to_follow
    )
    
    if success:
        print(f"You are now following {username_to_follow}.")
    else:
        print(f"Failed to follow {username_to_follow}. User might not exist or you're already following them.")
    
    return ctx, True

# Unfollow a user (UC-6)
def unfollowUser(ctx: Context) -> Tuple[Optional[Context], bool]:
    username_to_unfollow = input("Enter username to unfollow: ")
    
    success = Neo4jConnection.get_instance().unfollow_user(
        ctx.user["username"], username_to_unfollow
    )
    
    if success:
        print(f"You have unfollowed {username_to_unfollow}.")
    else:
        print(f"Failed to unfollow {username_to_unfollow}. User might not exist or you might not be following them.")
    
    return ctx, True

# View friends/connections (UC-7)
def viewConnections(ctx: Context) -> Tuple[Optional[Context], bool]:
    print("1. View users you follow")
    print("2. View your followers")
    choice = input("Choose an option: ")
    
    if choice == "1":
        connections = Neo4jConnection.get_instance().get_following(ctx.user["username"])
        connection_type = "following"
    elif choice == "2":
        connections = Neo4jConnection.get_instance().get_followers(ctx.user["username"])
        connection_type = "followers"
    else:
        print("Invalid option.")
        return ctx, True
    
    if connections is None:
        print("Failed to retrieve connections.")
        return ctx, True
    
    if len(connections) == 0:
        print(f"You have no {connection_type}.")
        return ctx, True
    
    print(f"\n--- Your {connection_type.capitalize()} ---")
    for user in connections:
        print(f"Username: {user['username']}, Name: {user['name']}")
    
    return ctx, True

# View mutual connections (UC-8)
def viewMutualConnections(ctx: Context) -> Tuple[Optional[Context], bool]:
    other_username = input("Enter username to find mutual connections with: ")
    
    # Don't compare with yourself
    if other_username == ctx.user["username"]:
        print("Cannot find mutual connections with yourself.")
        return ctx, True
    
    mutual_connections = Neo4jConnection.get_instance().get_mutual_connections(
        ctx.user["username"], other_username
    )
    
    if mutual_connections is None:
        print("Failed to retrieve mutual connections.")
        return ctx, True
    
    if len(mutual_connections) == 0:
        print(f"You have no mutual connections with {other_username}.")
        return ctx, True
    
    print(f"\n--- Mutual Connections with {other_username} ---")
    for user in mutual_connections:
        print(f"Username: {user['username']}, Name: {user['name']}")
    
    return ctx, True

# Get friend recommendations (UC-9)
def getFriendRecommendations(ctx: Context) -> Tuple[Optional[Context], bool]:
    print("Fetching friend recommendations...")
    
    recommendations = Neo4jConnection.get_instance().get_friend_recommendations(
        ctx.user["username"]
    )
    
    if recommendations is None:
        print("Failed to retrieve recommendations.")
        return ctx, True
    
    if len(recommendations) == 0:
        print("No recommendations found.")
        return ctx, True
    
    print("\n--- Friend Recommendations ---")
    for user in recommendations:
        print(f"Username: {user['username']}, Name: {user['name']}")
        if 'common_connections' in user:
            print(f"Common connections: {user['common_connections']}")
    
    return ctx, True

# Search for a user (UC-10)
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

# View most popular users (UC-11)
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

# Menu for guests (not logged in)
# The Tuple has two elements, the first is an optional Context storing user information 
# The second is a boolean indicating if the program should continue running
# The _ parameter means that we don't care about the value passed in
def guest_menu(_: Context) -> Tuple[Optional[Context], bool]:
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    ctx = None

    # Note that match is basically the same as a switch statement in other languages
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

# Menu for logged-in users
# Note that the Context is passed in as an argument to the function 
def user_menu(ctx: Context) -> Tuple[Optional[Context], bool]:
    if ctx is None:
        print("No user context found. Please log in.")
        return None, True
    print("1. View Profile")
    print("2. Edit Profile")
    print("3. Follow User")
    print("4. Unfollow User")
    print("5. View Connections")
    print("6. View Mutual Connections")
    print("7. Get Friend Recommendations")
    print("8. Search User")
    print("9. View Most Popular Users")
    print("0. Logout")

    match input("Choose an option: "):
        case "1":
            getProfile(ctx)
        case "2":
            updateProfile(ctx)
        case "3":
            followUser(ctx)
        case "4":
            unfollowUser(ctx)
        case "5":
            viewConnections(ctx)
        case "6":
            viewMutualConnections(ctx)
        case "7":
            getFriendRecommendations(ctx)
        case "8":
            searchUser(ctx)
        case "9":
            viewMostPopularUsers(ctx)
        case "0":
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
