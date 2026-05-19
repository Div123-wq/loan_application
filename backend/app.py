import os
import sys
# Ensure backend directory is in python path for serverless imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Serve static files from the frontend directory
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload

# Vercel's serverless environment is read-only except for /tmp
if os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV'):
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
else:
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except OSError:
    pass # In strict environments, ignore if we can't create it, we'll use in-memory anyway

@app.route('/')
def serve_index():
    """Serve the landing index.html by default."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Fallback route to serve static html files like dashboard.html, simulator.html, etc."""
    return send_from_directory(app.static_folder, path)


# Register blueprints
from routes.upload import upload_bp
from routes.analyze import analyze_bp
from routes.simulator import simulator_bp
from routes.compare import compare_bp
from routes.chat import chat_bp
from routes.auth import auth_bp

app.register_blueprint(upload_bp)
app.register_blueprint(analyze_bp)
app.register_blueprint(simulator_bp)
app.register_blueprint(compare_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(auth_bp)


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "LoanLens AI"})


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Max 32MB allowed."}), 413


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
