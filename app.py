from flask import Flask, request, jsonify
import requests
import mysql.connector

app = Flask(__name__)

# ---------------------------
# Configure MySQL
# ---------------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="your_database"
)
cursor = db.cursor(dictionary=True)

# ---------------------------
# Route to handle AI requests
# ---------------------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("question")  # Sent from script.js

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        # Send request to the third-party endpoint
        url = f"https://api.dreaded.site/api/chatgpt?text={user_input}"
        response = requests.get(url)
        response.raise_for_status()
        answer = response.text

        # Optional: Save question and answer to database
        insert_query = "INSERT INTO chat_history (question, answer) VALUES (%s, %s)"
        cursor.execute(insert_query, (user_input, answer))
        db.commit()

        return jsonify({"answer": answer})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------
# Route to get chat history from DB
# ---------------------------
@app.route("/history", methods=["GET"])
def history():
    cursor.execute("SELECT * FROM chat_history ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)


