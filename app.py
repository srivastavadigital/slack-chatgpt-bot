from flask import Flask, request, jsonify
import openai
import requests
import os

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "xoxb-your-slack-token")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-your-openai-key")
openai.api_key = OPENAI_API_KEY

def send_slack_message(channel, text):
    requests.post("https://slack.com/api/chat.postMessage", headers={
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }, json={
        "channel": channel,
        "text": text
    })

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    event = data.get("event", {})
    user_text = event.get("text", "")
    channel = event.get("channel")

    if event.get("type") in ["app_mention", "message"]:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_text}]
            )
            reply = response.choices[0].message["content"]
            send_slack_message(channel, reply)
        except Exception as e:
            send_slack_message(channel, f"Error: {str(e)}")

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
