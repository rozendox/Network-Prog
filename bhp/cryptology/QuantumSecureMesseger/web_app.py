from flask import Flask, jsonify
from database import SessionLocal, Message

app = Flask(__name__)

@app.route("/messages", methods=["GET"])
def list_messages():
    db = SessionLocal()
    messages = db.query(Message).all()
    db.close()
    return jsonify([{"sender": messages.sender, "receiber":messages.receiver,
                     "content": messages.content.hex()} for messages in messages])

if __name__ == "__main__":
    app.run(debug=True, port = 5000)