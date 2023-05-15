import psycopg2

def unfollow(conn, uid):
    """
    Allows the user to unfollow another user via prompt.
    AUTHOR: Sam June - scj9703@rit.edu
    :param conn: The connection to the database
    :param uid: the uid of the logged in user
    :return: none
    """
    try:
        cursor = conn.cursor()
        email = input("Enter an email to search: ")

        cursor.execute("SELECT uid FROM \"user\" WHERE email = %s", (email,))
        uid_to_unfollow = cursor.fetchone()[0]

        # Check if the current user is already following the specified user
        cursor.execute("SELECT COUNT(*) FROM friends_with WHERE uid1 = %s AND uid2 = %s", (uid, uid_to_unfollow))
        count = cursor.fetchone()[0]
        if count == 0:
            print("Error: You are not following this user.")
        else:
            # Delete the row from the "Friends with" relation
            cursor.execute("DELETE FROM friends_with WHERE uid1 = %s AND uid2 = %s", (uid, uid_to_unfollow))
            print("You have unfollowed this user.")
            conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
