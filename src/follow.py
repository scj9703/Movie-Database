import psycopg2

def follow(conn, uid):
    """
    Allows the user to follow/friend another user via prompt.
    AUTHOR: Sam June - scj9703@rit.edu
    :param conn: The connection to the database
    :param uid: the uid of the logged in user
    :return: none
    """
    try:
        cursor = conn.cursor()
        email = input("Enter an email to search: ")

        cursor.execute("SELECT uid FROM \"user\" WHERE email = %s", (email,))
        uid_to_follow = cursor.fetchone()[0]

        # Check if the current user is already following the specified user
        cursor.execute("SELECT COUNT(*) FROM friends_with WHERE uid1 = %s AND uid2 = %s", (uid, uid_to_follow))
        count = cursor.fetchone()[0]
        if count > 0:
            print("Error: You are already following this user.")
        else:
            # Add a new row to the "Friends with" relation
            cursor.execute("INSERT INTO friends_with (uid1, uid2) VALUES (%s, %s)", (uid, uid_to_follow))
            print("You are now following this user.")
            conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
