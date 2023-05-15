import psycopg2

def profile(conn, uid):
    """
        Displays the user's number of collections, following, followers, and top 10 movies.
        AUTHOR: Samuel June - scj9703@rit.edu
        :param conn: Connection to the database
        :param uid: The logged in user's id
        :return: none
        """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM collection WHERE uid = %s", (uid,))
        num_collections = cursor.fetchone()[0]
        print(f"The user with uid {uid} has {num_collections} collections.")

        cursor.execute("SELECT COUNT(*) FROM friends_with WHERE uid1 = %s", (uid,))
        num_following = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM friends_with WHERE uid2 = %s", (uid,))
        num_followers = cursor.fetchone()[0]

        print(f"The user with uid {uid} is following {num_following} users.")
        print(f"The user with uid {uid} is being followed by {num_followers} users.")

        query = input("How do you want to display your top 10? 'rating', 'lastwatch', 'both'")
        if query == 'rating':
            cursor.execute(
                "SELECT movie.title, MAX(rates.rating) FROM movie JOIN rates ON movie.mid = rates.mid GROUP BY movie.title ORDER BY MAX(rates.rating) DESC LIMIT 10")
            top_movies = cursor.fetchall()

            # Print the top 10 movies by rating
            print("The top 10 movies by rating are:")
            for i, row in enumerate(top_movies):
                print(f"{i + 1}. {row[0]} (Rating: {row[1]})")

        elif query == 'lastwatch':
            cursor.execute(
                "SELECT movie.title, MAX(watches.last_watched) FROM movie JOIN watches ON movie.mid = watches.mid GROUP BY movie.title ORDER BY MAX(watches.last_watched) DESC LIMIT 10")
            top_movies = cursor.fetchall()

            # Print the top 10 movies by last watched
            print("The top 10 movies by last watched are:")
            for i, row in enumerate(top_movies):
                print(f"{i + 1}. {row[0]} (Last Watched: {row[1]})")

        elif query == 'both':
            cursor.execute(
                "SELECT movie.title, MAX(watches.last_watched), MAX(rates.rating) FROM movie JOIN watches ON movie.mid = watches.mid JOIN rates ON movie.mid = rates.mid GROUP BY movie.title ORDER BY MAX(watches.last_watched) DESC, MAX(rates.rating) DESC LIMIT 10")
            top_movies = cursor.fetchall()

            print("The top 10 movies by a combination of last watched and rating, are:")
            for i, row in enumerate(top_movies):
                print(f"{i + 1}. {row[0]} (Last Watched: {row[1]}, Rating: {row[2]})")
        else:
            print("Error: That was not a valid input.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
