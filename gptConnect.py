from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key="GPT API KEY"
)

# 초기 상활 설정 및 첫 번째 질문 예시
message = [
        {"role": "system", "content": "You are a helpful cafe clerk. And your customer is blind and korean."},
        {"role": "user", "content": "안녕하세요. 아이스 아메리카노 한 잔 주세요"}
]

chat_completion = client.chat.completions.create(
    messages=message,
    model="gpt-4o",
)

answer = chat_completion.choices[0].message.content

# 응답 출력
print(answer)

# 대화 내역 업데이트
message.append({"role": "assistant", "content": answer})
message.append({"role": "user", "content": "그리고 카푸치노도 한잔 주세요"})

chat_completion = client.chat.completions.create(
    messages=message,
    model="gpt-4o",
)

answer = chat_completion.choices[0].message.content

# 응답 출력
print(answer)