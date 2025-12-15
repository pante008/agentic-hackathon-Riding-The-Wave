from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "Flask app is running"})

@app.route('/api/process_message', methods=['POST'])
def process_message_api():
    data = request.get_json() if request.is_json else request.form
    text_content = data.get('text_content', '')
    
    return jsonify({
        "message": "API endpoint is available",
        "text_received": text_content
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

