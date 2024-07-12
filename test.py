from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key= ""
)

structured_message = [
        {"role": "system", "content": "You are a helpful cafe clerk. "
                                      "There is a customer in front of you. "
                                      "You should take the order. The order must include the type of coffee, "
                                      "the size of the coffee, and the quantity. If the customer forgets to tell you "
                                      "specific details, you should ask them back. "
                                      "Structure the order like this: {type: {type}, size: {size}, quantity: {quantity}}"
                                      "if order is complete, you must return only the order."
         }
    ]

# chat_completion = client.chat.completions.create(
#     messages= structured_message,
#     model="gpt-4o"
# )

# while True :
#     user_chat = input("User: ")
#     if user_chat == "exit":
#         break
#     else :
#         structured_message.append({"role": "user", "content": user_chat})
#
#     chat_completion = client.chat.completions.create(
#         messages= structured_message,
#         model="gpt-4o"
#     )
#     print(chat_completion.choices[0].message.content)

def call_gpt(category, menu):
    while True :
        user_chat = input("User: ")
        if user_chat == "exit":
            break

        else :
            structured_message = [{"role": "system", "content": """You are a helpful café clerk. Customers chat, 
            so not all inputs will be orders. If an input is not an order, you must return only [this is not an order] 
            and ignore it. If the input is an order, you should take the order. 
            The order must include the type of coffee, the size of the coffee, and the quantity. 
            If the customer forgets to provide specific details, you should ask them for the missing information. 
            Structure the order like this: {type: {type}, size: {size}, quantity: {quantity}}. 
            If the order is complete, you must return only the order."""
             }]

            structured_message.append({"role": "user", "content": user_chat})

            chat_completion = client.chat.completions.create(
            messages=structured_message,
            model="gpt-4o"
        )
            print(chat_completion.choices[0].message.content)

call_gpt("coffee, bread, baverage", "iced americano, scone, lemonade")