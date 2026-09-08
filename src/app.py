from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "https://supply-chain-analytics-engine.vercel.app/"])
@app.route('/')
def index():
    return jsonify({
        "message": "Supply Chain Analytics API is running",
        "endpoints": [
            "/api/health",
            "/api/stats/summary",
            "/api/stats/regions",
            "/api/stats/shipping-modes",
            "/api/stats/categories",
            "/api/stats/status",
        ]
    })
def get_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))


def fetch_all(query):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/api/stats/regions')
def region_stats():
    data = fetch_all("SELECT order_region, total_orders, total_sales, avg_order_value FROM region_stats ORDER BY total_sales DESC")
    return jsonify(data)


@app.route('/api/stats/shipping-modes')
def shipping_stats():
    data = fetch_all("SELECT shipping_mode, total_shipments, late_risk_pct, avg_days_actual, avg_days_scheduled FROM shipping_mode_stats ORDER BY late_risk_pct DESC")
    return jsonify(data)


@app.route('/api/stats/categories')
def category_stats():
    data = fetch_all("SELECT category_name, total_orders, total_sales FROM category_stats ORDER BY total_sales DESC")
    return jsonify(data)


@app.route('/api/stats/status')
def status_stats():
    data = fetch_all("SELECT order_status, order_count FROM status_stats ORDER BY order_count DESC")
    return jsonify(data)


@app.route('/api/stats/summary')
def summary():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(total_orders), SUM(total_sales) FROM region_stats")
    total_orders, total_sales = cur.fetchone()
    conn.close()
    return jsonify({
        "total_orders": total_orders,
        "total_sales": round(float(total_sales), 2) if total_sales else 0,
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)