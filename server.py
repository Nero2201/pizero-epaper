from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
import os
import epd_7in3e_test as epd

app = Flask(__name__)
UPLOAD_FOLDER = "/home/pi/my_epaper/uploads"
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
            #progressBar { width: 100%; height: 20px; background: #eee; border-radius: 10px; overflow: hidden; display: none; }
            #bar { height: 100%; width: 0%; background: #4CAF50; }
            #displayBtn { display: none; margin-top: 20px; padding: 10px 20px; }
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
        <div id="progressBar"><div id="bar"></div></div>
        <img id="preview" src="">
        <button id="displayBtn">Anzeigen</button>

        <script>
            const form = document.getElementById('uploadForm');
            const progressBar = document.getElementById('progressBar');
            const bar = document.getElementById('bar');
            const preview = document.getElementById('preview');
            const fileInput = document.getElementById('fileInput');
            const displayBtn = document.getElementById('displayBtn');
            let lastFilename = null;
            let lastMode = null;

            fileInput.addEventListener('change', function() {
                const file = fileInput.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        preview.style.display = "block";
                    }
                    reader.readAsDataURL(file);
                }
            });

            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(form);
                progressBar.style.display = "block";
                bar.style.width = "0%";

                const xhr = new XMLHttpRequest();
                xhr.open("POST", "/upload");
                xhr.upload.onprogress = function(e) {
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
                        displayBtn.style.display = "inline-block";
                    } else {
                        alert("Fehler beim Hochladen!");
                    }
                };
                xhr.send(formData);
            });

            displayBtn.addEventListener('click', function() {
                fetch("/display", {
                    method: "POST",
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: lastFilename, mode: lastMode })
                }).then(r => {
                    if (r.ok) {
                        displayBtn.innerText = "Angezeigt!";
                        setTimeout(() => window.location.href = "/", 5000);
                    } else {
                        alert("Fehler beim Anzeigen!");
                    }
                });
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
    return jsonify({"filename": filename, "mode": mode})

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
