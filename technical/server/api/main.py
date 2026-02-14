from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import psycopg2
import redis
import os
import ssl
import sys

app = Flask(__name__)

# PostgreSQL connection
try:
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=os.environ.get('POSTGRES_PORT', 5432),
        dbname=os.environ.get('POSTGRES_DB', 'espdb'),
        user=os.environ.get('POSTGRES_USER', 'espuser'),
        password=os.environ.get('POSTGRES_PASSWORD', '')
    )
    cur = conn.cursor()
except Exception as e:
    print(f"[PostgreSQL] Connection error: {e}")
    sys.exit(1)

# Redis connection
try:
    r = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379)
    r.ping()
except Exception as e:
    print(f"[Redis] Connection error: {e}")
    sys.exit(1)

# MQTT setup
mqtt_client = mqtt.Client()

# Set username/password if required
mqtt_client.username_pw_set(
    os.environ.get("MQTT_USERNAME"),
    os.environ.get("MQTT_PASSWORD")
)

# TLS setup
mqtt_client.tls_set(
    ca_certs=os.environ.get("MQTT_CA"),
    tls_version=ssl.PROTOCOL_TLSv1_2
)

try:
    mqtt_client.connect(
        os.environ['MQTT_BROKER'],
        int(os.environ['MQTT_PORT']),
        60
    )
    mqtt_client.loop_start()
except Exception as e:
    print(f"❌ MQTT connection failed: {e}")

@app.route('/api/send', methods=['POST'])
def send_to_esp():
    data = request.json
    topic = data.get('topic')
    message = data.get('message')
    if not topic or not message:
        return jsonify({"error": "Missing topic or message"}), 400
    mqtt_client.publish(topic, message)
    return jsonify({"status": "sent", "topic": topic, "message": message})

@app.route('/api/state', methods=['GET'])
def get_state():
    cur.execute("SELECT * FROM esp_state ORDER BY timestamp DESC LIMIT 1;")
    row = cur.fetchone()
    if row:
        return jsonify({"id": row[0], "state": row[1], "timestamp": row[2].isoformat()})
    else:
        return jsonify({"status": "no data"}), 404

@app.route('/api/state', methods=['POST'])
def save_state():
    state = request.json.get('state')
    if not state:
        return jsonify({"error": "Missing 'state'"}), 400
    cur.execute("INSERT INTO esp_state (state) VALUES (%s) RETURNING id;", (state,))
    conn.commit()
    return jsonify({"status": "stored", "state": state})

@app.route('/api/temp', methods=['POST'])
def store_temp_data():
    key = request.json.get('key')
    value = request.json.get('value')
    if not key or not value:
        return jsonify({"error": "Missing 'key' or 'value'"}), 400
    r.set(key, value)
    return jsonify({"status": "stored", "key": key, "value": value})

@app.route('/api/temp/<key>', methods=['GET'])
def get_temp_data(key):
    value = r.get(key)
    if value:
        return jsonify({"key": key, "value": value.decode()})
    else:
        return jsonify({"status": "not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
