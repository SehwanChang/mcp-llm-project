import os
from flask import Flask, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATA_DIR = os.environ.get('DATA_DIR', '/data')
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/health')
def health():
    return jsonify({'status':'ok'})

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(DATA_DIR)
    return jsonify({'files': files})

@app.route('/files/<path:filename>', methods=['GET'])
def get_file(filename):
    safe = secure_filename(filename)
    path = os.path.join(DATA_DIR, safe)
    if not os.path.exists(path):
        abort(404)
    return send_from_directory(DATA_DIR, safe)

@app.route('/upload', methods=['POST'])
def upload():
    payload = request.json or {}
    filename = payload.get('filename')
    content = payload.get('content')
    if not filename or content is None:
        return jsonify({'error':'filename and content required'}), 400
    safe = secure_filename(filename)
    path = os.path.join(DATA_DIR, safe)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return jsonify({'saved': safe}), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
