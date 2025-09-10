import requests
import json

def ask_ai(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3:latest", "prompt": prompt},
            stream=True,
            timeout=10
        )
        result = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                result += data.get("response", "")
        return result
    except requests.exceptions.RequestException as e:
        return f"AI Error: {e}"

response = ask_ai("Tell me a joke")
print("Assistant says:", response.strip())
