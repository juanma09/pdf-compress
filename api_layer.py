from flask import Flask, request, jsonify
import time
import os
from base64_converter import base64_to_file, file_to_base64
from compress_layer import reduce
from utils import check_ttl, get_size_stats

app = Flask(__name__)

# Ensure an 'uploads' directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

OUTPUT_FOLDER = 'outputs'
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/', methods=["GET"])
def home():
    return jsonify({"status": "pdf-compress running"})

@app.route('/compress-pdf', methods=['POST'])
def upload_base64_file():
    data = request.get_json()

    if not data or 'file_b64' not in data:
        return jsonify({"error": "No base64 string provided"}), 400

    try:
        # 1. Get the base64 string
        b64_string = data['file_b64']
        
        # 2. Generate a filename based on current timestamp
        # Format: 1707012345.pdf
        timestamp = int(time.time())
        filename = f"{timestamp}.pdf"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        output_filepath = os.path.join(OUTPUT_FOLDER, filename)

        base64_to_file(b64_string, filepath)


        reduce(filepath, output_filepath)
        diff, percentage = get_size_stats(filepath, output_filepath)

        result = file_to_base64(output_filepath)
        check_ttl(UPLOAD_FOLDER, 3600)
        check_ttl(OUTPUT_FOLDER, 3600)
        
        return jsonify({
            "message": "File reduced successfully",
            "output": result,
            "diff_bits": diff,
            "percentage": percentage
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Listen on all interfaces so Docker can route traffic
    app.run(host='0.0.0.0', port=5000)