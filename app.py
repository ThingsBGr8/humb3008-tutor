import os
import json
import requests
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from GitHub Pages

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')

# ── Health check ──
@app.route('/')
def index():
    return jsonify({'status': 'ok', 'service': 'HUMB3008 tutor proxy'})

# ── Anthropic proxy ──
@app.route('/api/chat', methods=['POST'])
def chat():
    if not ANTHROPIC_API_KEY:
        return jsonify({'error': 'Anthropic API key not configured'}), 500
    try:
        data = request.get_json()
        res = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            },
            json=data,
            timeout=60
        )
        return Response(res.content, status=res.status_code, mimetype='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── ElevenLabs TTS proxy ──
@app.route('/api/tts/<voice_id>', methods=['POST'])
def tts(voice_id):
    if not ELEVENLABS_API_KEY:
        return jsonify({'error': 'ElevenLabs API key not configured'}), 500
    try:
        data = request.get_json()
        res = requests.post(
            f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',
            headers={
                'xi-api-key': ELEVENLABS_API_KEY,
                'Content-Type': 'application/json'
            },
            json=data,
            timeout=30
        )
        return Response(
            res.content,
            status=res.status_code,
            mimetype='audio/mpeg'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
