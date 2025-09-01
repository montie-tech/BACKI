from flask import Flask, request, jsonify
import requests
import mysql.connector
from mysql.connector import Error
import socket

app = Flask(__name__)

# ---------------------------
# Configure MySQL
# ---------------------------
try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        database="recipe_db"
    )
    cursor = db.cursor(dictionary=True)
    print("✅ Connected to MySQL")
except Error as e:
    print(f"⚠️ Could not connect to MySQL: {e}")
    db = None
    cursor = None

# ---------------------------
# Route to handle AI requests with fallback
# ---------------------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("question", "").strip()

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # First attempt: online AI endpoint
    try:
        url = f"https://api.dreaded.site/api/chatgpt?text={user_input}"
        response = requests.get(url, timeout=5)  # 5s timeout
        response.raise_for_status()
        answer = response.text

        # Save to MySQL if available
        if db and cursor:
            try:
                insert_query = "INSERT INTO chat_history (question, answer) VALUES (%s, %s)"
                cursor.execute(insert_query, (user_input, answer))
                db.commit()
            except Error as e:
                print(f"⚠️ Failed to save to MySQL: {e}")

        return jsonify({"answer": answer, "source": "online"})

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Online AI failed: {e}")

        # Fallback: search MySQL for previous answers
        if db and cursor:
            try:
                cursor.execute(
                    "SELECT answer FROM chat_history WHERE question LIKE %s ORDER BY id DESC LIMIT 1",
                    (f"%{user_input}%",)
                )
                row = cursor.fetchone()
                if row:
                    return jsonify({"answer": row["answer"], "source": "database (fallback)"})
                else:
                    return jsonify({"answer": "Sorry, no answer available.", "source": "fallback"}), 200
            except Error as e:
                print(f"⚠️ Failed to query MySQL fallback: {e}")
                return jsonify({"answer": "Sorry, no answer available.", "source": "fallback"}), 200

        # If no DB fallback
        return jsonify({"answer": "Sorry, AI service is unavailable and no database fallback.", "source": "none"}), 503

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

# ---------------------------
# Helper: Find a free port
# ---------------------------
def find_free_port(default_port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('', default_port))
        port = default_port
    except OSError:
        s.bind(('', 0))  # Bind to a random free port
        port = s.getsockname()[1]
    finally:
        s.close()
    return port

# ---------------------------
# Run app
# ---------------------------
if __name__ == "__main__":
    port = find_free_port(5000)
    print(f"🚀 Flask server running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

