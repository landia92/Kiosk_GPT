import mysql.connector

# 데이터베이스 연결 설정
config = {
    'user': 'admin',
    'password': 'xmrtnanswk1',
    'host': '35.227.189.156',  # Cloud SQL 인스턴스의 외부 IP
    'database': 'sungbin_house'
}

# 데이터베이스에 연결
conn = mysql.connector.connect(**config)
cursor = conn.cursor()


# 데이터 가져오기
cursor.execute("SELECT id FROM category")
result = cursor.fetchall()

# 결과 출력
for row in result:
    print(row)

# 연결 종료
cursor.close()
conn.close()