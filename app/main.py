from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status':'ok'})

@app.route('/process', methods=['POST'])
def process():
    data = request.json or {}
    url = data.get('url')
    if not url:
        return jsonify({'error':'url required'}), 400
    # Placeholder: actual extraction, summarization, quiz generation to be implemented
    return jsonify({'message':'received', 'url': url})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
