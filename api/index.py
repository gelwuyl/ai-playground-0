import json
import os
import base64

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


def handler(request):
    """
    Vercel Python serverless function.
    Endpoint: /api
    Body: { "prompt": "...", "mode": "text" | "image" }
    Returns: { "text": "..." } or { "image": "base64...", "mime": "image/png" }
    """
    # CORS preflight
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": "",
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed"}),
        }

    # Parse request body
    try:
        raw_body = request.body
        if isinstance(raw_body, bytes):
            raw_body = raw_body.decode("utf-8")
        body = json.loads(raw_body) if raw_body else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON body"}),
        }

    prompt = (body.get("prompt") or "").strip()
    mode = body.get("mode", "text")

    if not prompt:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing or empty 'prompt' field"}),
        }

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Server misconfigured: GEMINI_API_KEY missing"}),
        }

    if genai is None:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "google-genai package not installed"}),
        }

    try:
        if mode == "image":
            return _generate_image(prompt, api_key)
        return _generate_text(prompt, api_key)
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"API call failed: {str(e)}"}),
        }


def _generate_text(prompt, api_key):
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1024,
        ),
    )

    text = response.text or ""

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"text": text, "model": "gemini-2.0-flash"}),
    }


def _generate_image(prompt, api_key):
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    image_data = None
    mime = "image/png"
    text_data = None

    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            image_data = base64.b64encode(part.inline_data.data).decode("utf-8")
            mime = part.inline_data.mime_type or "image/png"
        if part.text:
            text_data = part.text

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({
            "image": image_data,
            "mime": mime,
            "text": text_data,
            "model": "gemini-2.0-flash-image",
        }),
    }
