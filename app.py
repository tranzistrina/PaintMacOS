from flask import Flask, render_template, request, jsonify
import base64

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/image")
def image_info():
    data = request.get_json(silent=True) or {}
    image = data.get("image", "")
    if not image.startswith("data:image/"):
        return jsonify({"ok": False, "error": "Invalid image data"}), 400
    try:
        _, encoded = image.split(",", 1)
        base64.b64decode(encoded, validate=True)
    except Exception:
        return jsonify({"ok": False, "error": "Invalid image data"}), 400
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7789, debug=False)
