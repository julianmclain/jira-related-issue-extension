import sqlite_vss

from database import connect_to_db


db_name = "jira-issue-embeddings.db"
conn = connect_to_db(db_name)
sqlite_vss.load(conn)

q1 = """
    select rowid, distance
    from vss_issues
    where vss_search(
        embedding,
        (select embedding from issues where id = 1)
    )
    limit 20
"""
r1 = conn.execute(q1).fetchall()
# print(r1)

q2 = """
    with matches as (
        select 
            rowid, 
            distance
        from vss_issues
    where vss_search(
        embedding,
        (select embedding from issues where rowid = 1)
    )
    limit 20
    )

    select
        issues.rowid,
        issues.summary,
        matches.distance
    from matches
    left join issues on issues.rowid = matches.rowid
"""
r2 = conn.execute(q2).fetchall()
print(r2)
