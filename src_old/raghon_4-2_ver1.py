import os
from dotenv import load_dotenv

load_dotenv()

# os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGCHAIN_API_KEY"] = userdata.get("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "agent-book"

from langchain_openai import OpenAI

model = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
ai_message = model.invoke("こんにちは")
print(ai_message)