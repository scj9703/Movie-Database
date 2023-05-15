import psycopg2
from datetime import date
from newReleases import newReleases

def popular(conn, uid):
    """
    Allows the user to view popular movies based on friends and recent watches
    AUTHOR: Justin Ceiley - jgc9449@rit.edu
    :param conn: Connection to the database
    :param uid: The logged in user's id
    :return: none
    """

    try:
        cursor = conn.cursor()
        which = input("Would you like to view popular with friends, popular in the last 90 days"
                        "top 5 movies of the month or recommended (friends / recent / month / recommended) ")
        print()
        
        if which == "friends":
            cursor.execute("select movie.title, avg(rates.rating) as avg_rating from friends_with "
                           "inner join rates on friends_with.uid2 = rates.uid inner join movie on rates.mid = movie.mid "
                           "where friends_with.uid1 = %s "
                           "group by movie.title "
                           "order by avg_rating desc limit 20;", (uid,))
            
            for row in cursor.fetchall():
                print("Title: " + row[0] + " Rating: {rating:.2f}".format(rating=row[1]))
        elif which == "recent":
            cursor.execute("select movie.title, avg(rates.rating) as avg_rating from \"user\""
                            "inner join rates on \"user\".uid = rates.uid "
                            "inner join watches on \"user\".uid = watches.uid "
                            "inner join movie on watches.mid = movie.mid "
                            "where watches.last_watched > current_date + interval '-90 days' "
                            "group by movie.title "
                            "order by avg_rating desc limit 20;")
            
            for row in cursor.fetchall():
                print("Title: " + row[0] + " Rating: {rating:.2f}".format(rating=row[1]))
        elif which == "month":
            newReleases(conn)

        elif which == "recommended":
            cursor.execute("select movie.title, avg(rates.rating) as avg_rating from \"user\" "
                            "inner join rates on \"user\".uid = rates.uid "
                            "inner join watches on \"user\".uid = watches.uid "
                            "inner join movie on watches.mid = movie.mid "
                            "inner join has on movie.mid = has.mid "
                            "inner join genre on has.gid = genre.gid "
                            "where genre.name in (select genre.name from \"user\" "
                            "    inner join rates on \"user\".uid = rates.uid "
                            "    inner join watches on \"user\".uid = watches.uid "
                            "    inner join movie on watches.mid = movie.mid "
                            "    inner join has on has.mid = movie.mid "
                            "    inner join genre on has.gid = genre.gid "
                            "    where \"user\".uid = %s "
                            "    group by (genre.name) "
                            "    order by avg(rates.rating) desc "
                            "    limit 5) "
                            "group by movie.title "
                            "order by avg_rating desc limit 5;", (uid, ))
            for row in cursor.fetchall():
                print("Title: " + row[0] + " Rating: {rating:.2f}".format(rating=row[1]))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
