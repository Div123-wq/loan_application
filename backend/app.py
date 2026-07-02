import os
import sys
# Ensure backend directory is in python path for serverless imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Serve static files from the frontend directory
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Supported languages
app.config.setdefault('LANGUAGES', {
    'en': 'English',
    'kn': 'Kannada',
    'hi': 'Hindi',
    'mr': 'Marathi',
    'te': 'Telugu',
    'ta': 'Tamil',
    'ml': 'Malayalam'
})

# Simple message translations for small backend responses (avoid Flask-Babel incompatibility)
MESSAGES = {
    'en': { 'status_msg': 'FinScan AI Backend API is running.' },
    'hi': { 'status_msg': 'FinScan AI बैकएंड एपीआई चल रही है।' },
    'kn': { 'status_msg': 'FinScan AI ಬ್ಯಾಕ್‌ಎಂಡ್ API ನಡೆಯುತ್ತಿದೆ.' },
    'mr': { 'status_msg': 'FinScan AI बॅकेंड API चालू आहे.' },
    'te': { 'status_msg': 'FinScan AI బ్యాక్‌ఎండ్ API నడుస్తోంది.' },
    'ta': { 'status_msg': 'FinScan AI பின்-முனை API இயங்குகிறது.' },
    'ml': { 'status_msg': 'FinScan AI ബാക്കെൻഡ് API പ്രവർത്തിക്കുന്നു.' }
}

def get_preferred_lang(request):
    lang = request.args.get('lang') or request.cookies.get('lang')
    if lang and lang in app.config['LANGUAGES']:
        return lang
    return request.accept_languages.best_match(list(app.config['LANGUAGES'].keys())) or 'en'

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
    """Serve a basic status message for the root URL."""
    from flask import request
    lang = get_preferred_lang(request)
    msg = MESSAGES.get(lang, MESSAGES['en'])['status_msg']
    return jsonify({"status": "ok", "message": msg})


@app.route('/api/set_language', methods=['GET'])
def set_language():
    """Set the preferred language via cookie. Use `?lang=hi` etc."""
    from flask import request, make_response
    lang = request.args.get('lang')
    if not lang or lang not in app.config['LANGUAGES']:
        return jsonify({"error": "invalid_language", "supported": list(app.config['LANGUAGES'].keys())}), 400
    resp = make_response(jsonify({"status": "ok", "lang": lang}))
    resp.set_cookie('lang', lang, max_age=60*60*24*365)
    return resp

@app.errorhandler(404)
def not_found(e):
    """Fallback route to return 404 JSON for unknown routes."""
    return jsonify({"error": "Not Found", "message": "The requested URL was not found on the server."}), 404


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
    return jsonify({"status": "ok", "service": "FinScan AI"})


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Max 32MB allowed."}), 413


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
