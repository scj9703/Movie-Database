"""
File: main.py
Description: The main file for the application program used to access the movie database.
Author: Jacob Hubbard (jmh5319)
"""
import codecs
import hashlib
from datetime import date

import psycopg2
from sshtunnel import SSHTunnelForwarder

import sys
import os

from follow import follow
from unfollow import unfollow
from rate import rate
from search import search
from popular import popular
from newReleases import newReleases
from userprofile import profile

dbName = "p320_02"


def prompt_user_for_command(prompt, command_set):
    """
    Prompt the user for a command from a given set of commands. This function will only return when the user enters a
    command that is in the command set.
    :param prompt: The prompt presented to the user. It should list all valid commands.
    :param command_set: The set of valid commands.
    :return: A command chosen by the user from the command set.
    """
    while True:
        user_command = input(prompt).strip()
        if user_command in command_set:
            return user_command
        else:
            print("Invalid command:", user_command)


def prompt_user_for_uid(prompt):
    """
    Prompts the user to enter a valid user ID. This function will not return until a valid ID is entered. Note that this
    function does not check if the given user ID actually exists; it only checks that the user ID is an integer.
    :param prompt: The prompt presented to the user.
    :return: A valid user ID given by the user.
    """
    while True:
        print()
        print()
        string_uid = input(prompt).strip()
        try:
            uid = int(string_uid)
            return uid
        except:
            print()
            print()
            print("Invalid UID detected, please try again.")
            # the loop continues until a valid uid is generated


def salt_and_hash_password(password, username):
    """
    Salts and hashes the password. Characters from the username are inserted into the password in an alternating manner.
    :param password: The plaintext password to be salted and hashed.
    :param username: The username of the user the password belongs to.
    :return: The salted and hashed password.
    """
    x = 0
    salted_password = ""
    while x < len(password) and x < len(username):
        salted_password += password[x]
        salted_password += username[x]
        x += 1
    while x < len(password):
        salted_password += password[x]
        x += 1
    while x < len(username):
        salted_password += username[x]
        x += 1
    byte_salted_password = codecs.encode(salted_password, "utf-8")
    hash_alg = hashlib.sha3_256()
    hash_alg.update(byte_salted_password)
    secured_password = hash_alg.hexdigest()
    return secured_password


def account_creation_screen(conn):
    """
    This screen handles creation of new user accounts.
    :param conn: The connection to the database.
    :return: None.
    """
    cursor = conn.cursor()

    print()
    print()
    username = input("Please enter a username:").strip()
    password = salt_and_hash_password(input("Please enter a password:").strip(), username)
    first_name = input("Please enter your first name:").strip()
    last_name = input("Please enter your last name:").strip()
    email_addr = input("Please enter your email address:").strip()

    cursor.execute("SELECT MAX(uid) AS maxval FROM \"user\";")
    largest_id = cursor.fetchone()
    uid = largest_id[0] + 1

    creation_date = date.today()

    cursor.execute("INSERT INTO \"user\"(uid, username, password, first_name, last_name, email, creation_date, last_log_on) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
                   (uid, username, password, first_name, last_name, email_addr, creation_date, creation_date))

    print()
    print("User account created!")
    print("You may now login using the ID number", uid)

    conn.commit()


def logged_in_screen(conn, uid):
    """
    This screen handles actions the user can take while logged into their account.
    :param conn: The connection to the database.
    :param uid: The user ID of the current user.
    :return: None.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM \"user\" WHERE uid = %s;", (uid,))
    username_table_entry = cursor.fetchone()
    username = username_table_entry[0]
    print("Hello there, " + username + "!")

    while True:
        print()
        print()
        user_command = prompt_user_for_command("Please type a command. Valid commands are 'follow', 'unfollow', 'rate', 'search', 'collection', 'popular', 'newReleases', 'profile', 'logout'. ",
                                               {"follow", "unfollow", "rate", "search", "logout", "collection", "popular", "newReleases", "profile"})
        if user_command == "follow":
            follow(conn, uid)
        elif user_command == "unfollow":
            unfollow(conn, uid)
        elif user_command == "rate":
            rate(conn, uid)
        elif user_command == "collection":
            collection_screen(conn, uid)
        elif user_command == "search":
            search(conn, uid)
        elif user_command == "popular":
            popular(conn, uid)
        elif user_command == "newReleases":
            newReleases(conn)
        elif user_command == "profile":
            profile(conn, uid)
        else:  # logout command
            return


def attempt_login_screen(conn):
    """
    This screen handles attempts to login to the system.
    :param conn: The connection to the database.
    :return: None.
    """
    cursor = conn.cursor()

    uid = prompt_user_for_uid("Please enter your user ID:")
    username = ""
    cursor.execute("SELECT username FROM \"user\" WHERE uid = %s", (uid,))
    username_row = cursor.fetchone()
    if username_row is not None:
        username = username_row[0]
        print(username)
    password = salt_and_hash_password(input("Please enter your password:").strip(), username)

    cursor.execute("SELECT * FROM \"user\" WHERE uid = %s AND password = %s;", (uid, password))

    if cursor.fetchone() is not None:
        print()
        print()
        print("Login successful.")
        login_date = date.today()
        cursor.execute("UPDATE \"user\" SET last_log_on = %s WHERE uid = %s;", (login_date, uid))
        conn.commit()
        logged_in_screen(conn, uid)
    else:
        print("Login was invalid.")


def initial_screen(conn):
    """
    This screen is presented to the user when they first run the application. It allows users to create new accounts or
    login to existing ones.
    :param conn: The connection to the database.
    :return: None.
    """
    while True:
        print()
        print()
        user_command = prompt_user_for_command("Type 'create' to create a new user account, 'login' to sign into an"
                                           " existing account, or 'quit' to close the application:",
                                           {"create", "login", "quit"})
        if user_command == "create":
            account_creation_screen(conn)
        elif user_command == "login":
            attempt_login_screen(conn)
        else:  # quit command
            return


def connect_to_db(username, password):
    """
    This function establishes a connection to the movie database.
    :param username: The RIT username of the person logging into the database.
    :param password: The RIT CS password of the person logging into the database.
    :return: None.
    """
    try:
        print(username)
        print(password)
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=username.strip(),
                                ssh_password=password.strip(),
                                remote_bind_address=('localhost', 5432)) as server:
            server.start()
            print("SSH tunnel established")
            params = {
                'database': dbName,
                'user': username,
                'password': password,
                'host': 'localhost',
                'port': server.local_bind_port
            }

            conn = psycopg2.connect(**params)
            print("Database connection established")

            initial_screen(conn)  # pass the cursor to the initial screen
    except Exception as e:
        print(e)
        print("Connection failed")
    finally:
        conn.close()

def collection_screen(conn, uid):
    cursor = conn.cursor()

    while True:
        print()
        print()
        user_command = prompt_user_for_command("'create' to create a new collection\n‘delete' to delete a collection"
                                               "\n'list' to see a"
                                           " list of of your collections\n'rename' to rename a collection'\n"
                                           "'add' to add movies\n'remove' to remove movies"
                                           "\n'quit' to close the application: ",
                                           {"create", "delete", "rename", "list", "add", "remove", "quit"})
        
        if user_command == "create":
            print()
            collection_name = input("Enter a name for the collection: ")
            if collection_name != "":
                cursor.execute("SELECT name from collection where name=%s", (collection_name,))
                existing_name = cursor.fetchone()
                if not existing_name:
                    cursor.execute("SELECT MAX(cid) AS maxval FROM collection;")
                    largest_id = cursor.fetchone()
                    if largest_id[0] == None:
                        cid = 1
                    else:
                        cid = largest_id[0] + 1

                    cursor.execute("INSERT INTO collection (cid, uid, name) VALUES (%s, %s, %s);",
                                (cid, uid, collection_name))
                    print(f"Created {collection_name} collection")
                    conn.commit()
                else:
                    print("Collection name already taken")
        elif user_command == "delete":
            print()
            collection_name = input("Enter the name of the collection to delete: ")
            if collection_name != "":
                cursor.execute("SELECT name from collection where name=%s", (collection_name,))
                existing_name = cursor.fetchone()
                if existing_name:
                    cursor.execute("SELECT cid from collection where name=%s", (collection_name,))
                    cid = cursor.fetchone()
                    cursor.execute("delete from contains where cid=%s", (cid[0],))
                    cursor.execute("delete from collection where cid=%s and name=%s;",
                                (cid[0], collection_name))
                    print(f"Deleted {collection_name} collection")
                    conn.commit()
                else:
                    print("Collection doesn't exist")
        elif user_command == "rename":
            print()
            collection_name = input("Enter the name for the collection to rename: ")
            if collection_name != "":
                cursor.execute("SELECT name from collection where name=%s", (collection_name,))
                existing_name = cursor.fetchone()
                if existing_name:
                    update_name = input("Enter new name for the collection: ")
                    cursor.execute("SELECT name from collection where name=%s", (update_name,))
                    update_existing_name = cursor.fetchone()
                    if not update_existing_name:
                        cursor.execute("update collection set name=%s where name=%s", (update_name, collection_name))
                        conn.commit()
                        print(f"Updated collection {collection_name} to {update_name}")
                    else:
                        print("Collection with that name already exists")

                else:
                    print("Collection doesn't exist")
        elif user_command == "list":
            print()
            cursor.execute("select name, count(contains.mid), sum(movie.length) from collection join contains on collection.cid = contains.cid join movie on contains.mid = movie.mid where uid=%s group by collection.name", (uid,))
            collections = cursor.fetchall()
            for collection in collections:
                print(collection[0])
                print("    Total Movies: " + str(collection[1]))
                print("    Total Runtime: " + str(collection[2]) + " minutes")
        elif user_command == "add":
            print()
            movie_name = input("Enter the name of the movie to be added: ")
            cursor.execute("SELECT mid from movie where title=%s", (movie_name,))
            mid = cursor.fetchone()
            if mid:
                print()
                collection_name = input("Enter the name of the collection to alter: ")
                cursor.execute("SELECT cid from collection where name=%s", (collection_name,))
                cid = cursor.fetchone()
                if cid:
                    cursor.execute("INSERT into contains (mid, cid) values (%s, %s)", (mid[0], cid[0]))
                    conn.commit()
                    print(f"Added {movie_name} to collection {collection_name}")
                else:
                    print("Invalid collection name")
            else:
                print("Invalid movie name")
        elif user_command == "remove":
            print()
            movie_name = input("Enter the name of the movie to be removed: ")
            cursor.execute("SELECT mid from movie where title=%s", (movie_name,))
            mid = cursor.fetchone()
            if mid:
                print()
                collection_name = input("Enter the name of the collection to alter: ")
                cursor.execute("SELECT cid from collection where name=%s", (collection_name,))
                cid = cursor.fetchone()
                if cid:
                    cursor.execute("delete from contains where mid=%s and cid=%s", (mid[0], cid[0]))
                    conn.commit()
                    print(f"Removed {movie_name} from collection {collection_name}")
                else:
                    print("Invalid collection name")
            else:
                print("Invalid movice name")
        else:
            return


if __name__ == '__main__':
    if os.path.exists('../.env'):
            with open('../.env', 'r') as f:
                lines = f.readlines()
                username = lines[0].strip()
                password = lines[1].strip()
                print("username: " + username)
                print("password: " + password)
                connect_to_db(username, password)
    elif len(sys.argv) != 3:
        print("invalid arguments")
    
    else:
        connect_to_db(sys.argv[1], sys.argv[2])
