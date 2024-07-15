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

# 초기 상활 설정 및 첫 번째 질문 예시
message = [
        {"role": "system", "content":
            "You are a helpful cafe clerk."
            "And your customer is korean and old or disabled."
            "If customer mention Category you should answer 'findCategory'"
         },
        {"role": "user", "content": "안녕하세요. 아이스 아메리카노 한 잔 주세요"}
]

# 데이터 가져오기
cursor.execute("SELECT name FROM category")
result = cursor.fetchall()

# 결과 출력
for row in result:
    print(row[0])

# 연결 종료
cursor.close()
conn.close()