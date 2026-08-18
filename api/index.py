from flask import Flask, request, jsonify
import os
import base64

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

app = Flask(__name__)

@app.route('/api', methods=['POST', 'OPTIONS'])
def api_handler():
    if request.method == 'OPTIONS':
        return _cors_response('', 200)
    
    data = request.get_json(silent=True) or {}
    prompt = (data.get('prompt') or '').strip()
    mode = data.get('mode', 'text')
    
    if not prompt:
        return _json_response({'error': 'Missing or empty prompt field'}, 400)
    
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return _json_response({'error': 'Server misconfigured: GEMINI_API_KEY missing'}, 500)
    
    if not HAS_GENAI:
        return _json_response({'error': 'google-genai package not installed'}, 500)
    
    try:
        if mode == 'image':
            return _generate_image(prompt, api_key)
        return _generate_text(prompt, api_key)
    except Exception as e:
        return _json_response({'error': f'API call failed: {str(e)}'}, 500)

def _generate_text(prompt, api_key):
    client = genai.Client(api_key=api_key)
    result = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=1024),
    )
    return _json_response({'text': result.text or '', 'model': 'gemini-2.5-flash'}, 200)

def _generate_image(prompt, api_key):
    client = genai.Client(api_key=api_key)
    result = client.models.generate_content(
        model='gemini-2.0-flash-preview-image-generation',
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE']),
    )
    image_data = None
    mime = 'image/png'
    text_data = None
    for part in result.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            image_data = base64.b64encode(part.inline_data.data).decode('utf-8')
            mime = part.inline_data.mime_type or 'image/png'
        if part.text:
            text_data = part.text
    return _json_response({
        'image': image_data, 'mime': mime, 'text': text_data, 'model': 'gemini-2.0-flash-image'
    }, 200)

def _json_response(data, status=200):
    resp = jsonify(data)
    resp.status_code = status
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

def _cors_response(body, status=200):
    from flask import Response
    resp = Response(body, status=status, mimetype='text/plain')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

# WSGI entry point
if __name__ == '__main__':
    app.run()
