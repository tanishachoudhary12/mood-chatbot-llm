from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.9, max_tokens=20)

res = llm.invoke("Write a poem on ai")
print(res.content)