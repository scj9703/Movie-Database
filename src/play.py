import psycopg2
from datetime import date
def play(conn, uid):
    """
    Allows the user to watch a movie, or all movies in a collection.
    AUTHOR: Sam June - scj9703@rit.edu
    :param conn: Connection to the database
    :param uid: The logged in user's id
    :return: none
    """
    try:
        cursor = conn.cursor()
        userinput = input("What would you like to play? Valid inputs are 'movie' and 'collection'")
        if userinput == "collection":
            cid = input("Select the collection id of the collection you would like to play: ")
            watched = date.today()
            cursor.execute("""SELECT movie.mid FROM movie JOIN contains ON movie.mid = contains.mid WHERE contains.cid = %s""", (cid))
            count = 0
            for row in cursor:
                mid = row[0]
                cursor.execute("SELECT COUNT(*) FROM watches WHERE uid = %s AND mid = %s", (uid, mid))
                result = cursor.fetchone()
                if result[0] > 0:
                    cursor.execute("UPDATE watches SET last_watched = %s WHERE uid = %s AND mid = %s",(watched, uid, mid))
                    conn.commit()
                else:
                    cursor.execute("INSERT INTO watches (mid, last_watched, uid) VALUES (%s, %s, %s)", (mid, watched, uid))
                    conn.commit()
                count = count + 1
            if count > 0:
                print("Collection has been played.")
            else:
                print("Error: The collection was empty or did not exist")
        elif userinput == "movie":
            mid = input("Select the movie id of the movie you would like to play: ")
            cursor.execute("SELECT COUNT(*) FROM watches WHERE uid = %s AND mid = %s", (uid, mid))
            result = cursor.fetchone()
            watched = date.today()
            if result[0] > 0:
                cursor.execute("UPDATE watches SET last_watched = %s WHERE uid = %s AND mid = %s", (watched, uid, mid))
                conn.commit()
                print("You have replayed this movie.")
            else:
                cursor.execute("INSERT INTO watches (mid, last_watched, uid) VALUES (%s, %s, %s)", (mid, watched, uid))
                conn.commit()
                print("Movie has been played.")
        else:
            print("Error: That was not a valid input.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
