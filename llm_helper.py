from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize the Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Optional: Test llm directly
if __name__ == "__main__":
    response = llm.invoke("Two most important ingredients in samosa are ")
    print(response.content)
