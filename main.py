from flask import Flask, Response, request, jsonify
from dotenv import load_dotenv
import json
import requests
import os

app = Flask(__name__)

load_dotenv()

base_id = os.getenv('BASE_ID')
api_key = os.getenv('API_KEY')

def make_comment(part=None, is_fructed=False):
    try:
        part = f"часть тела на снимке - {['рука', 'нога', 'таз', 'плечо'][part]},"
    except:
        part = 'на котором мы не смогли определить часть тела'

    fruc_status = 'перелом' if is_fructed else 'перелом отсутствует'

    prompt = {
        "modelUri": f"gpt://{base_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "600"
        },
        "messages": [
            {
                "role": "system",
                "text": """Ты система, которая пишет комментарии к результатам рентгена, внутри больницы. 
                           Придумай краткий и информативный комментарий к данным, полученным после рентгеновского анализа. 
                           Комментарий должен быть полезен пациенту, но может быть полезен и сотруднику больницы. 
                           Он должен быть кратким и включать наблюдение за наличием или отсутствием перелома, и рекомендуемыми действиями."""
            },
            {
                "role": "user",
                "text": f"Комментарий к результату рентгеновского анализа, {part} {fruc_status}."
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key " + api_key
    }

    response = requests.post(url, headers=headers, json=prompt)
    return response.json()  # Return JSON response

@app.route("/make_comment", methods=['POST'])
def comment():
    try:
        part = request.json.get('part', None)
        is_fructed = request.json.get('is_fructed', False)
        
        response = make_comment(part=part, is_fructed=is_fructed)

        res = json.dumps(response["result"]["alternatives"][0]["message"]["text"], ensure_ascii=False).encode('utf8')
        return Response(res, status=200)    
    except Exception as e:
        return jsonify(message=f'Something went wrong: {str(e)}'), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
