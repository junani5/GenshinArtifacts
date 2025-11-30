import sqlite3

def init_db():
    # genshin_build.db 라는 SQLite 파일 생성 (없으면 새로 만들어짐)
    conn = sqlite3.connect("genshin_build.db")

    # foreign_keys 옵션은 커넥션마다 다시 켜줘야 해서 한번 더 실행
    conn.execute("PRAGMA foreign_keys = ON;")

    # schema.sql 읽어서 그대로 실행
    with open("create_tables.sql", "r", encoding="utf-8") as f:
        schema = f.read()
    conn.executescript(schema)

    conn.commit()
    conn.close()
    print("DB 초기화 완료! (genshin_build.db 생성됨)")

if __name__ == "__main__":
    init_db()
