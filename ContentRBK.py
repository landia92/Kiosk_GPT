import os
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 환경 변수에서 API 키를 가져옵니다.
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수를 설정해야 합니다.")

client = OpenAI(
    api_key=api_key
)

structured_message = [
    {"role": "system", "content": "당신은 카페 직원입니다. " # system 역할로, AI의 행동을 지시->카페 직원
                                  "당신 앞에 고객이 있습니다. "
                                  "고객은 한국인일 가능성이 높습니다."

                                  # 시스템 메시지에 예외 상황 처리 추가
                                  "고객이 주문과 관련 없는 질문을 한다면, "
                                  "예를 들어 카페 정보, 위치, 영업 시간 등을 물어보면, 도움 되는 답변을 제공하세요. "
                                  "카페와 완전히 무관한 질문이라면, "
                                  "정중하게 카페 관련 문의만 도와드릴 수 있다고 알려주세요. "

                                  "당신은 주문을 받아야 합니다. "
                                  "카페에는 각 카테고리마다 여러 메뉴 항목이 있습니다. "
                                  "메뉴 항목이 포함되어야 하며, 메뉴 항목 없이 주문할 수 없습니다. "

                                  # 주문 취소
                                  "고객은 주문 과정 중 언제든지 주문을 취소할 수 있습니다. "

                                  "메뉴의 온도(뜨겁게 또는 차갑게), 크기, 수량 등의 주문 세부 사항을 물어보세요. "
                                  "고객이 특정 세부 사항을 말하는 것을 잊었다면, 다시 물어보세요. "
                                  "고객이 이미 세부 사항을 지정했다면, 다시 묻지 마세요. "
                                  "주문을 다음과 같이 구조화하세요: "
                                  "{타입: {type}, 온도: {temperature}, 크기: {size}, 수량: {quantity}, 가격: {price}} "

                                  "주문이 완료되면, 주문만 반환해야 합니다. "

                                  "한 메뉴 항목의 주문을 완료한 후, 고객은 다른 항목을 선택할 수 있습니다. "
                                  "따라서, 추가로 주문할 것이 있는지 물어보세요. "

                                  # 주문 요약 및 최종 확인
                                  "고객이 더 이상 주문할 것이 없다고 말하면, "
                                  "주문 세부 사항과 총 가격을 반복하여 확인을 요청하세요. "
                                  # 최종 주문 키워드
                                  "고객이 주문 확인이 맞다는 응답을 하면, "
                                  "'Order Complete'를 출력하여 주문 과정이 완료되었음을 자동으로 표시하세요. "

     },
    {"role": "assistant", "content": "안녕하세요. 주문을 도와드릴까요?"} #assistant 역할로, 처음 사용자에게 보일 인사 메시지를 설정
]

chat_completion = client.chat.completions.create(
    messages= structured_message,
    model="gpt-4o"
)

print(structured_message[-1]['content']) #리스트의 마지막 메시지인 "안녕하세요 주문을 도와드릴까요?"를 출력

while True :
    user_chat = input("User: ")
    if user_chat == "exit":
        break
    else :
        structured_message.append({"role": "user", "content": user_chat})

    chat_completion = client.chat.completions.create(
        messages= structured_message,
        model="gpt-4o"
    )
    response = chat_completion.choices[0].message.content
    print(response)
    structured_message.append({"role": "assistant", "content": response})

