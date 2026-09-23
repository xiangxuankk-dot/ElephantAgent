from openai import OpenAI

# client = OpenAI(
#     api_key="", # 请替换成您的ModelScope Access Token
#     base_url="https://api-inference.modelscope.cn/v1/"
# )
# response = client.responses.create(
#     model="Qwen/Qwen3.8-Flash-Next",
#     input="hello"
# )
# print(response.model_dump_json())

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

response = client.responses.create(
    model="gpt-3.5-turbo",
    #tools=[{"type": "web_search"}],
    input="What was a positive news story from today?",
)

print(response.output_text)

