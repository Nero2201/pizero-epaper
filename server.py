from flask import Flask, request, jsonify, send_from_directory
from PIL import Image, ImageOps
import os
import epd_7in3e_test as epd

app = Flask(__name__)
UPLOAD_FOLDER = "/home/pi/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return '''
    <html>
    <head>
        <title>Bild auf E-Paper hochladen</title>
        <style>
            body { font-family: Arial; background: #f0f0f0; text-align: center; padding: 40px; }
            form { background: #fff; display: inline-block; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px #aaa; }
            input[type="file"], input[type="submit"] { margin: 10px; }
            #preview { max-width: 300px; margin: 10px auto; display: none; }

            #overlay {
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: rgba(0,0,0,0.5);
                display: none;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                color: white;
                font-size: 20px;
                z-index: 9999;
            }

            #progressBar {
                width: 300px;
                height: 20px;
                background: #444;
                border-radius: 10px;
                overflow: hidden;
                margin-top: 20px;
            }

            #bar {
                height: 100%;
                width: 0%;
                background: #4CAF50;
                transition: width 0.3s;
            }

            #doneSection {
                display: none;
                flex-direction: column;
                align-items: center;
                gap: 20px;
            }

            #backButton {
                padding: 10px 20px;
                font-size: 16px;
                background: #4CAF50;
                border: none;
                border-radius: 5px;
                color: white;
                cursor: pointer;
            }

            #backButton:hover {
                background: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>Bild auf E-Paper hochladen</h1>
        <form id="uploadForm">
            <input type="file" name="file" id="fileInput" required><br>
            <label><input type="radio" name="mode" value="fit" checked> Fit</label>
            <label><input type="radio" name="mode" value="fill"> Fill</label>
            <label><input type="radio" name="mode" value="stretch"> Stretch</label><br>
            <input type="submit" value="Hochladen">
        </form>
        <img id="preview" src="">

        <div id="overlay">
            <div id="uploading">Bild wird hochgeladen und angezeigt...</div>
            <div id="progressBar"><div id="bar"></div></div>
            <div id="doneSection">
                <div>✔️ Fertig!</div>
                <button id="backButton" onclick="window.location.href='/'">Zurück</button>
            </div>
        </div>

        <script>
        const form = document.getElementById('uploadForm');
        const overlay = document.getElementById('overlay');
        const uploadingText = document.getElementById('uploading');
        const progressBar = document.getElementById('progressBar');
        const bar = document.getElementById('bar');
        const preview = document.getElementById('preview');
        const fileInput = document.getElementById('fileInput');
        const doneSection = document.getElementById('doneSection');
    
        // NEU:
        const displayButton = document.createElement("button");
        displayButton.innerText = "Anzeigen";
        displayButton.style = "padding: 10px 20px; margin-top: 20px; font-size: 16px;";
        displayButton.onclick = () => {
            overlay.style.display = "flex";
            progressBar.style.display = "block";
            bar.style.width = "100%";
            uploadingText.innerText = "Bild wird auf dem E-Paper angezeigt...";
    
            fetch("/display", {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: lastFilename, mode: lastMode })
            }).then(r => {
                if (r.ok) {
                    progressBar.style.display = "none";
                    uploadingText.style.display = "none";
                    doneSection.style.display = "flex";
                    displayButton.remove();  // Button wieder entfernen
                } else {
                    uploadingText.innerText = "Fehler beim Anzeigen!";
                }
            });
        }
    
        let lastFilename = null;
        let lastMode = null;
    
        fileInput.addEventListener('change', function () {
            const file = fileInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.src = e.target.result;
                    preview.style.display = "block";
                }
                reader.readAsDataURL(file);
            }
        });
    
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(form);
            overlay.style.display = "flex";
            progressBar.style.display = "block";
            bar.style.width = "0%";
            doneSection.style.display = "none";
    
            const xhr = new XMLHttpRequest();
            xhr.open("POST", "/upload");
            xhr.upload.onprogress = function (e) {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    bar.style.width = percent + "%";
                }
            };
            xhr.onload = function() {
                if (xhr.status === 200) {
                    const res = JSON.parse(xhr.responseText);
                    lastFilename = res.filename;
                    lastMode = res.mode;
            
                    // Vorschau anzeigen (vom Server bearbeitetes Bild)
                    preview.src = "/preview.jpg?" + new Date().getTime();
                    preview.style.display = "block";
            
                    // Fortschrittsanzeige fertig machen
                    bar.style.width = "100%";
                    uploadingText.innerText = "Bild wird auf dem E-Paper angezeigt...";
            
                    // Jetzt Bild automatisch auf E-Paper anzeigen
                    fetch("/display", {
                        method: "POST",
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ filename: lastFilename, mode: lastMode })
                    }).then(r => {
                        if (r.ok) {
                            progressBar.style.display = "none";
                            uploadingText.style.display = "none";
                            doneSection.style.display = "flex";
                        } else {
                            uploadingText.innerText = "Fehler beim Anzeigen!";
                        }
                    });
                } else {
                    overlay.innerHTML = "<h2 style='color:red;'>Fehler beim Hochladen</h2>";
                }
            };
            xhr.send(formData);
        });
    </script>
    </body>
    </html>
    '''

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    mode = request.form.get("mode", "fit")
    filename = f"upload_{mode}.jpg"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    # Bild für Vorschau bearbeiten
    try:
        img = Image.open(path).convert("L")  # Graustufen
        img.thumbnail((800, 480))            # auf E-Paper-Größe skalieren (optional)
        # img = ImageOps.invert(img)         # Beispiel für Invertierung
        preview_path = os.path.join(UPLOAD_FOLDER, "preview.jpg")
        img.save(preview_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "filename": filename,
        "mode": mode
    })

@app.route("/display", methods=["POST"])
def display_file():
    data = request.get_json()
    filename = data["filename"]
    mode = data["mode"]
    path = os.path.join(UPLOAD_FOLDER, filename)
    try:
        img = Image.open(path)
        epd.display(img, mode)
        return "OK"
    except Exception as e:
        return f"Fehler: {e}", 500

@app.route("/preview.jpg")
def get_preview():
    return send_from_directory(UPLOAD_FOLDER, "preview.jpg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
