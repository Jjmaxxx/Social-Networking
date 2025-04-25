from neo4j_connection import Neo4jConnection
import getpass
import os

conn = Neo4jConnection()



current_user = None
current_username = None

while True:
    if not current_user:
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")
        os.system("clear")
        if choice == "1":
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

        elif choice == "2":
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            user = conn.authenticate_user(username, password)
            if user:
                current_user = user
                current_username = user['username']
                print(f"Login successful. Welcome, {current_user['name']}!")
            else:
                print("Invalid credentials.")

        elif choice == "3":
            print("Exiting the program.")
            break
        else:
            print("Invalid option.")
    
    else:
        print("\n--- Logged in as:", current_username, "---")
        print("1. View Profile")
        print("2. Edit Profile")
        print("3. Logout")
        choice = input("Choose an option: ")
        os.system("clear")
        if choice == "1":
            profile = conn.get_profile(current_username)
            if profile:
                print("\n--- Your Profile ---")
                print("Name:", profile["name"])
                print("Username:", profile["username"])
                print("Email:", profile["email"])
                print("Bio:", profile["bio"])
            else:
                print("Profile not found.")

        elif choice == "2":
            new_name = input("New name: ")
            new_bio = input("New bio: ")
            conn.update_profile(current_username, new_name, new_bio)
            print("Profile updated.")

        elif choice == "3":
            current_user = None
            current_username = None
            print("Logged out.")
        else:
            print("Invalid option.")

conn.close()