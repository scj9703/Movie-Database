
import psycopg2

def search(conn, uid):
    """
    Allows a user to search for movies in various ways.
    AUTHOR: Sam June - scj9703@rit.edu
    :param conn: The connection to the database
    :param uid: The logged in user's ID
    :return: none
    """
    try:
        cursor = conn.cursor()
        userinput = input("What would you like to search? Valid inputs are 'name' 'releasedate' 'castmember' 'studio' 'genre' ")
        match userinput:
            case "name":
                query = input("Input a movie name to search: ")
                cursor.execute("SELECT movie.mid, movie.title, movie.release_date, movie.length, movie.MPAA_Rating, genre.name, studio.name FROM movie JOIN has on movie.mid = has.mid JOIN produces ON movie.mid = produces.mid JOIN studio ON produces.sid = studio.sid JOIN genre on has.gid = genre.gid WHERE title LIKE %s ORDER BY title ASC, release_date ASC", (query,))
            case "releasedate":
                query = input("Input a release date to search (ex: 2023-01-01): ")
                cursor.execute("SELECT movie.mid, movie.title, movie.release_date, movie.length, movie.MPAA_Rating, genre.name, studio.name FROM movie JOIN has on movie.mid = has.mid JOIN produces ON movie.mid = produces.mid JOIN studio ON produces.sid = studio.sid JOIN genre on has.gid = genre.gid WHERE release_date = %s ORDER BY title ASC, release_date ASC", (query,))
            case "castmember":
                query = input("Input a cast member's pid to search: ")
                cursor.execute("""
                    SELECT movie.mid, movie.title, movie.release_date, movie.length, movie.MPAA_Rating, genre.name
                    FROM movie
                    JOIN actor ON movie.mid = actor.mid
                    JOIN has ON movie.mid = has.mid
                    JOIN genre ON has.gid = genre.gid
                    JOIN produces ON movie.mid = produces.mid
                    JOIN studio ON produces.sid = studio.sid
                    WHERE actor.pid = %s
                    UNION
                    SELECT movie.mid, movie.title, movie.release_date, movie.length, movie.MPAA_Rating, genre.name
                    FROM movie
                    JOIN director ON movie.mid = director.mid
                    JOIN has ON movie.mid = has.mid
                    JOIN genre ON has.gid = genre.gid
                    JOIN produces ON movie.mid = produces.mid
                    JOIN studio ON produces.sid = studio.sid
                    WHERE director.pid = %s
                    ORDER BY title ASC, release_date ASC
                """, (query, query))
            case "studio":
                query = input("Input a studio's sid to search: ")
                cursor.execute("""SELECT movie.mid, movie.title, movie.release_date, movie.length, movie.MPAA_Rating, genre.name
                                   FROM movie
                                   JOIN produces ON movie.mid = produces.mid
                                   JOIN studio ON produces.sid = studio.sid
                                   JOIN has ON movie.mid = has.mid
                                   JOIN genre ON has.gid = genre.gid
                                   WHERE produces.sid = %s
                                   ORDER BY movie.title ASC, movie.release_date ASC""", (query,))
            case "genre":
                query = input("Input a genre's gid to search: ")
                cursor.execute(
                    "SELECT movie.mid, movie.title, movie.release_date, movie.length, movie.MPAA_Rating, genre.name, studio.name FROM movie JOIN has ON movie.mid = has.mid JOIN produces ON movie.mid = produces.mid JOIN studio ON produces.sid = studio.sid JOIN genre on has.gid = genre.gid WHERE has.gid = %s ORDER BY title ASC, release_date ASC",
                    (query,))
            case _:
                print("Error: Invalid input")
                return

        results = cursor.fetchall()
                
        custom_sort = input("Would you like to sort by a different value? yes/no ")
        if custom_sort == "yes":
            asc_or_desc = input("Would you like to sort descending? (default ascending) yes/no ")
            direction = False if asc_or_desc=="no" else True
            sort_method = input("How would you like to sort (movie name, studio, genre or release year) ")
            match sort_method:
                case "movie name":
                    results = sorted(results, key=lambda x: x[1], reverse=direction)
                case "studio":
                    results = sorted(results, key=lambda x: x[6], reverse=direction)
                case "genre":
                    results = sorted(results, key=lambda x: x[5], reverse=direction)
                case "release year":
                    results = sorted(results, key=lambda x: x[2], reverse=direction)
                case _:
                    print("Invalid sort method")
                    return
                
        for row in results:
            mid, title, release_date, length, mpaa_rating, genre, studio = row
            print(f"Title: {title}")
            # get the list of actors for this movie
            cursor.execute(
                "SELECT person.first_name, person.last_name FROM actor JOIN person ON actor.pid = person.pid WHERE actor.mid = %s",
                (mid,))
            actors = cursor.fetchall()  # fetch all rows returned by the query

            # get the list of directors for this movie
            cursor.execute(
                "SELECT person.first_name, person.last_name FROM director JOIN person ON director.pid = person.pid WHERE director.mid = %s",
                (mid,))
            directors = cursor.fetchall()

            # print the results
            print("Actors:")
            for actor in actors:
                print(f"{actor[0]} {actor[1]}")
            print("Directors:")
            for director in directors:
                print(f"{director[0]} {director[1]}")

            print(f"Length: {length}")
            print(f"MPAA Rating: {mpaa_rating}")
            cursor.execute("SELECT rating FROM rates WHERE uid = %s AND mid = %s", (uid, mid))
            row = cursor.fetchone()
            if row:
                rating = row[0]
                print(f"The rating for movie {mid} by user {uid} is {rating}.")
            else:
                print(f"You have not rated this movie.")
            print()


    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
