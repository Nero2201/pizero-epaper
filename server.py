from flask import Flask, request, jsonify
from PIL import Image
import io
import base64
import converter
import epd_7in3e_test as epd

app = Flask(__name__)

# RAM-Zwischenspeicher für das aktuell bearbeitete Bild
last_image_data = {}

@app.route("/")
def index():
    return '''
    <html>
    <head>
        <title>Bild auf E-Paper hochladen</title>
        <style>
            body {
                font-family: Arial;
                background: #f0f0f0;
                text-align: center;
                padding: 40px;
            }
            form {
                background: #fff;
                display: inline-block;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px #aaa;
            }
            input[type="file"], input[type="submit"] {
                margin: 10px;
            }
            #preview {
                max-width: 400px;
                margin: 20px auto;
                display: none;
            }
            #spinner {
                border: 8px solid #f3f3f3;
                border-top: 8px solid #4CAF50;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                margin: 20px auto;
                animation: spin 1s linear infinite;
                display: none;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            #displayBtn {
                display: none;
                padding: 10px 20px;
                font-size: 16px;
                background: #4CAF50;
                border: none;
                border-radius: 5px;
                color: white;
                cursor: pointer;
                margin-top: 20px;
            }
            #displayBtn:hover {
                background: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>Bild auf E-Paper vorbereiten</h1>
        <form id="uploadForm">
            <input type="file" name="file" id="fileInput" required><br>
            <label><input type="radio" name="mode" value="fit" checked> Fit</label>
            <label><input type="radio" name="mode" value="fill"> Fill</label>
            <label><input type="radio" name="mode" value="stretch"> Stretch</label><br>
        </form>
        <img id="preview" src="">
        <div id="spinner"></div>
        <button id="displayBtn">Anzeigen</button>

        <script>
            const fileInput = document.getElementById("fileInput");
            const modeInputs = document.querySelectorAll("input[name='mode']");
            const preview = document.getElementById("preview");
            const displayBtn = document.getElementById("displayBtn");
            const uploadForm = document.getElementById("uploadForm");
            const spinner = document.getElementById("spinner");

            function updatePreview() {
                const file = fileInput.files[0];
                if (!file) return;

                const formData = new FormData(uploadForm);

                // Spinner anzeigen, Vorschau bleibt sichtbar
                spinner.style.display = "block";
                displayBtn.style.display = "none";

                fetch("/preview", {
                    method: "POST",
                    body: formData
                })
                .then(r => r.json())
                .then(data => {
                    spinner.style.display = "none";

                    if (data.preview) {
                        preview.src = data.preview;
                        preview.style.display = "block";
                        displayBtn.style.display = "inline-block";
                    } else {
                        displayBtn.style.display = "none";
                    }
                })
                .catch(() => {
                    spinner.style.display = "none";
                    displayBtn.style.display = "none";
                });
            }

            fileInput.addEventListener("change", updatePreview);
            modeInputs.forEach(input => input.addEventListener("change", updatePreview));

            displayBtn.addEventListener("click", () => {
                fetch("/display", { method: "POST" })
                    .then(r => r.json())
                    .then(data => {
                        if (data.status === "ok") {
                            alert("Bild wird angezeigt!");
                            window.location.href = "/";
                        } else {
                            alert("Fehler beim Anzeigen: " + (data.error || "Unbekannter Fehler"));
                        }
                    })
                    .catch(err => {
                        alert("Fehler beim Senden: " + err);
                    });
            });
        </script>
    </body>
    </html>
    '''

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
