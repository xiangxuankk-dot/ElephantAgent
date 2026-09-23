import json
import os

import requests
from dotenv import load_dotenv

load_dotenv() # 加载.env文件到环境变量

BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")   # 兼容端点改这里
API_KEY  = os.environ.get("LLM_API_KEY")
MODEL    = os.environ.get("LLM_MODEL_ID", "gpt-4o-mini")


def get_weather(city: str, unit: str="celsius") -> str:
    return f"{city}:晴，26{unit}"

#构造tool
TOOLS=[
    {
        "type":"function",
        "function":{
            "name": "get_weather",
            "description": "查询指定城市的当前天气。当用户想知道某个城市的天气、温度时使用。",
            "parameters":{
                "type": "object",
                "properties":{
                    "city": {
                        "type": "string",
                        "description": "城市名，例如：北京、上海",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位，默认摄氏度",
                    },
                },
                "required": ["city"],
                "additionalProperties": False,
            }
        },
    }
]

AVAILABLE_TOOLS = {"get_weather": get_weather}   # 名字 -> 函数，手动分派


def chat(messages):
    r = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": messages,
             "tools": TOOLS,
            # "tool_choice": "auto"
            },
        timeout=60)
    r.raise_for_status()
    return r.json()

messages =[{"role":"user","content":"北京今天天气怎么样？用华氏也告诉我一下。"}]

data = chat(messages)
print(json.dumps(data, ensure_ascii=False, indent=2))
msg = data["choices"][0]["message"]

print("finish reason:", data["choices"][0]["finish_reason"])
print("tool_calls:", json.dumps(msg.get("tool_calls"),ensure_ascii=False,indent=2))

#解析参数
if msg.get("tool_calls"):
    msg_clean = {k: v for k,v in msg.items() if v is not None}
    messages.append(msg_clean)

    for tc in msg["tool_calls"]:
        fn = tc["function"]
        print(fn["arguments"])
        args = json.loads(fn["arguments"])
        result = AVAILABLE_TOOLS[fn["name"]](**args)
        messages.append({
            "role":"tool",
            "tool_call_id":tc["id"],
            "content":str(result),
        })

    final = chat(messages)["choices"][0]["message"]["content"]
    print("\n最终回答:", final)
