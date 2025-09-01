from flask import Flask, request, jsonify
import requests
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# ---------------------------
# Configure MySQL
# ---------------------------
try:
    db = mysql.connector.connect(
        host="127.0.0.1",    # Change if needed
        user="root",
        password="your_password",
        database="your_database"
    )
    cursor = db.cursor(dictionary=True)
    print("✅ Connected to MySQL")
except Error as e:
    print(f"⚠️ Could not connect to MySQL: {e}")
    db = None
    cursor = None

# ---------------------------
# Route to handle AI requests
# ---------------------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("question")

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        # Send request to third-party AI endpoint
        url = f"https://api.dreaded.site/api/chatgpt?text={user_input}"
        response = requests.get(url)
        response.raise_for_status()
        answer = response.text

        # Try saving to MySQL if available
        if db and cursor:
            try:
                insert_query = "INSERT INTO chat_history (question, answer) VALUES (%s, %s)"
                cursor.execute(insert_query, (user_input, answer))
                db.commit()
            except Error as e:
                print(f"⚠️ Failed to save to MySQL: {e}")

        return jsonify({"answer": answer})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"AI request failed: {e}"}), 500

# ---------------------------
# Route to get chat history from DB
# ---------------------------
@app.route("/history", methods=["GET"])
def history():
    if db and cursor:
        try:
            cursor.execute("SELECT * FROM chat_history ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            return jsonify(rows)
        except Error as e:
            return jsonify({"error": f"Failed to fetch history: {e}"}), 500
    else:
        return jsonify({"error": "Database not available"}), 503

if __name__ == "__main__":
    app.run(debug=True)
