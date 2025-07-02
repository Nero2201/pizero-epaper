from flask import Flask, request, jsonify, render_template
from PIL import Image
import io
import base64
import converter
import epd_7in3e_test as epd

app = Flask(__name__)

last_image_data = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/preview", methods=["POST"])
def preview():
    if "file" not in request.files:
        return jsonify({ "error": "Kein Bild erhalten" }), 400

    file = request.files["file"]
    mode = request.form.get("mode", "fit")

    try:
        img = Image.open(file.stream).convert("RGB")
        converted = converter.convert(img, mode)
        last_image_data["image"] = converted

        buf = io.BytesIO()
        converted.convert("RGB").save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        return jsonify({ "preview": f"data:image/jpeg;base64,{b64}" })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

@app.route("/display", methods=["POST"])
def display():
    img = last_image_data.get("image")
    if img is None:
        return jsonify({"error": "Kein Bild im Speicher"}), 400

    try:
        epd.display(img)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
