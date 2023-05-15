import psycopg2

def rate(conn, uid):
    """
    Allows the user to rate a movie via prompt.
    AUTHOR: Sam June - scj9703@rit.edu
    :param conn: The connection to the database
    :param uid: the uid of the logged in user
    :return: none
    """
    try:
        cursor = conn.cursor()
        
        mid = int(input("Enter the movie ID to rate: "))
        rating = int(input("Enter a rating for the movie (1-5): "))

        if rating < 1 or rating > 5:
            print("Error: Rating must be between 1 and 5.")
        else:
            # Insert a new row into the "rates" relation
            cursor.execute("INSERT INTO rates (uid, mid, rating) VALUES (%s, %s, %s)", (uid, mid, rating))
            print("Your rating has been recorded.")
            conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
