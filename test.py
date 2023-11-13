import sqlite3
import sqlite_vss


db_name = "jira-issue-embeddings.db"
db = sqlite3.connect(db_name)
sqlite_vss.load(db)
