from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

leaderboard = {}

def ask_ai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


@app.route("/webhook", methods=["POST"])
def webhook():
    incoming = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    resp = MessagingResponse()
    msg = resp.message()

    if incoming == ".menu":
        msg.body("""
╭──〔 RIO BOT 〕──⬡

AI:
.ai
.quiz
.plan
.pastpaper
.leaderboard
        """)

    elif incoming.startswith(".ai "):
        question = incoming[4:]
        msg.body(ask_ai(question))

    elif incoming.startswith(".quiz "):
        topic = incoming[6:]
        quiz = ask_ai(f"Create 5 MCQ quiz on {topic}")
        msg.body(quiz)
        leaderboard[sender] = leaderboard.get(sender, 0) + 10

    elif incoming.startswith(".plan"):
        msg.body(ask_ai("Create study timetable"))

    elif incoming.startswith(".pastpaper "):
        exam = incoming[11:]
        msg.body(f"Search PDF for {exam}")

    elif incoming == ".leaderboard":
        board = "\n".join(
            [f"{k}: {v}" for k, v in leaderboard.items()]
        ) or "No scores yet"
        msg.body(board)

    else:
        msg.body("Unknown command. Type .menu")

    return str(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
