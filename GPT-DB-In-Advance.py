from openai import OpenAI
import mysql.connector

# 데이터베이스 연결 설정
config = {
    'user': 'admin',
    'password': 'xmrtnanswk1',
    'host': '35.227.189.156',  # Cloud SQL 인스턴스의 외부 IP
    'database': 'sungbin_house'
}

client = OpenAI(
    api_key=""
)

# 데이터베이스에 연결
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

cursor.execute("SELECT name FROM category")
result = cursor.fetchall()
categoryText = ""
# 결과 출력
for row in result:
    categoryText = categoryText + row[0] + ", "

# 초기 상활 설정 및 첫 번째 질문 예시
structured_message = [
        {"role": "system", "content":
            "You are a helpful cafe clerk."
            "And your customer is korean and old or disabled."
            "The Categorys are " + categoryText + "so if customer mention Category you should answer them"
         }
]

while True :
    user_chat = input("User: ")
    if user_chat == "exit":
        break
    else :
        structured_message.append({"role": "user", "content": user_chat})

    chat_completion = client.chat.completions.create(
        messages=structured_message,
        model="gpt-4o"
    )
    print(chat_completion.choices[0].message.content)



# 연결 종료
cursor.close()
conn.close()