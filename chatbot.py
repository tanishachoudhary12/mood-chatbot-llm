from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage , SystemMessage 
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.9)

print("choose your ai mode")
print("press 1 for angry mode")
print("press 2 for flirty mode")
print("press 3 for funny mode")

choice = int(input("Tell your response :- "))

if choice == 1:
    mode = "You are a angry ai agent that answers questions in an angry way to a girl."
elif choice == 2:
    mode = "You are a flirty ai agent that answers questions in a flirty way to a girl."
elif choice == 3:                                   
    mode = "You are a funny ai agent that answers questions in a funny way to a girl."

messages = [
    SystemMessage(content=mode),
]
print("--------welcome type 0 to exit --------")
while True:
    
    prompt=input("You:")
    messages.append(HumanMessage(content=prompt))
    if prompt == "0":
        break
    
    
    res = llm.invoke(messages)
    messages.append(AIMessage(content=res.content))
    print("Bot :" , res.content)
