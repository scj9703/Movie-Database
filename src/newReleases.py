import datetime
import psycopg2
def newReleases(conn):
    """
    Shows the top 5 new releases of the month, ranked by avg rating.
    AUTHOR: Samuel June - scj9703@rit.edu
    :param conn: Connection to the database.
    :return: None
    """
    try:
        cursor = conn.cursor()
        now = datetime.datetime.now()
        month = now.month
        year = now.year

        # SQL query to get the top 5 new releases of the month, ordered by average rating
        cursor.execute("""
        SELECT m.title, m.release_date, AVG(r.rating) AS avg_rating
        FROM movie m
        JOIN rates r ON m.mid = r.mid
        WHERE EXTRACT(YEAR FROM m.release_date) = %s AND EXTRACT(MONTH FROM m.release_date) = %s
        GROUP BY m.mid
        ORDER BY avg_rating DESC
        LIMIT 5
        """, (year, month))

        # Fetch the results and print them
        results = cursor.fetchall()
        print("The top 5 releases of this month:")
        for i, row in enumerate(results):
            print(f"#{i + 1}: {row[0]} ({row[1].strftime('%Y-%m-%d')}): {row[2]:.2f}")


    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
