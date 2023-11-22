import sqlite3
import sqlite_vss

from database import connect_to_db

db_name = "jira-issue-embeddings.db"
conn = connect_to_db(db_name)
sqlite_vss.load(conn)

r = conn.execute("select summary from issues where id = 1;").fetchone()[0]
print(r)
q1 = """
    select rowid, distance
    from vss_issues
    where vss_search(
        embedding,
        (select embedding from issues where id = 1)
    )
    limit 20
"""
r2 = conn.execute(q1).fetchall()
print(r2)


q2 = """
    with matches as (
        select 
            rowid, 
            distance
        from vss_issues
    where vss_search(
        headline_embedding,
        (select headline_embedding from articles where rowid = 590)
    )
    limit 20
    )
    select
    articles.rowid,
    articles.headline,
    matches.distance
    from matches
    left join articles on articles.rowid = matches.rowid
"""
