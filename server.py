from flask import Flask, send_from_directory, request, jsonify
import sqlite3
import os

app = Flask(__name__, static_folder="web/static", static_url_path="/static")

# Ensure paths match workspace root
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "customer_analytics.db")

@app.route("/")
def index():
    """Serve the main landing page of the dashboard."""
    return send_from_directory(os.path.join(BASE_DIR, "web"), "index.html")

@app.route("/dashboard_data.json")
def dashboard_data():
    """Serve the pre-computed metrics JSON cache."""
    return send_from_directory(os.path.join(BASE_DIR, "web"), "dashboard_data.json")

@app.route("/api/query", methods=["POST"])
def execute_query():
    """Exposes an endpoint to run user queries on SQLite and return JSON data."""
    req_data = request.get_json()
    if not req_data or "query" not in req_data:
        return jsonify({"error": "No query provided"}), 400
        
    raw_query = req_data["query"].strip()
    
    # Simple Security Safeguard: check for SELECT or WITH queries only
    # First, strip single-line SQL comments (-- comment)
    lines = raw_query.split('\n')
    clean_lines = []
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line.startswith('--'):
            # Remove inline comments as well
            if '--' in line:
                line = line.split('--')[0]
            clean_lines.append(line)
            
    normalized_query = " ".join(clean_lines).strip().upper()
    
    # Must start with SELECT or WITH
    if not (normalized_query.startswith("SELECT") or normalized_query.startswith("WITH")):
        return jsonify({"error": "Query rejected. For safety and data integrity, only SELECT or WITH (read-only) queries are supported."}), 400
        
    # Check for modification commands anywhere in the query to prevent injection
    mod_keywords = ["INSERT ", "UPDATE ", "DELETE ", "DROP ", "ALTER ", "CREATE ", "TRUNCATE ", "REPLACE ", "GRANT "]
    if any(keyword in normalized_query for keyword in mod_keywords):
        return jsonify({"error": "Query rejected. Modifying SQL keywords (INSERT, UPDATE, DELETE, DROP, etc.) are strictly prohibited."}), 400
        
    if not os.path.exists(DB_PATH):
        return jsonify({"error": "Analytical database file not found. Run the data loading pipeline first."}), 500
        
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(raw_query)
        rows = cursor.fetchall()
        
        # Format results as a list of key-value dictionaries
        results = [dict(row) for row in rows]
        
        conn.close()
        return jsonify({"data": results})
        
    except sqlite3.Error as e:
        return jsonify({"error": f"SQLite Database Error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting AuraAnalytics Web Engine on http://0.0.0.0:{port}")
    print(f"Relational DB connected: {DB_PATH}")
    app.run(host="0.0.0.0", port=port, debug=True)

