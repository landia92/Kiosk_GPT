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
    {"role": "system", "content": "You are a helpful cafe clerk. " # system 역할로, AI의 행동을 지시->카페 직원
                                  "There is a customer in front of you. "
                                  "Your customer is likely to be Korean."

                                  "If the customer asks questions unrelated to ordering," # 시스템 메시지에 예외 상황 처리 추가
                                  "such as cafe information, location, opening hours, etc., provide helpful answers. "
                                  "If the question is completely unrelated to the cafe,"
                                  "politely inform them that you can only assist with cafe-related inquiries. "

                                  "You should take the order."
                                  "There are several menu items for each category in cafe."
                                  "The menu must be included, and an order cannot be placed without a menu item. "
                                  
                                  # 주문 취소
                                  "The customer can cancel the order at any time during the ordering process. "

                                  "Ask for order details such as"
                                  "temperature (hot or ice), size, and quantity of the menu. "
                                  "If the customer forgets to tell you specific details, you should ask them back. "
                                  "If the customer has already specified the details, do not ask again. "
                                  "Structure the order like this:"
                                  "{type: {type}, temperature: {temperature}, size: {size}, quantity: {quantity}} "
                                  "If the order is complete, you must return only the order. "

                                  # 비용 안내 추가
                                  
                                  "if order is complete, you must return only the order."

                                  "After completing the order for one menu item, the customer can choose another item. "
                                  "Therefore, you should ask if they would like to add anything else."

                                  "If the customer says there are no more orders,"
                                  "repeat the order details and ask for confirmation." # 주문 요약 및 최종 확인
                                   
                                   # 최종 주문 키워드
                                  "Once the confirmation is received from the customer, "
                                  "print 'Order Complete' to automatically indicate that the ordering process is finished."

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

