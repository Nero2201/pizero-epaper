from flask import Flask, request
from PIL import Image
import os
import epd_7in3e_test as epd

app = Flask(__name__)
UPLOAD_FOLDER = "/home/pi/my_epaper/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        mode = request.form["mode"]
        filename = f"upload_{mode}.jpg"
        path = os.path.join(UPLOAD_FOLDER, filename)

        img = Image.open(file)

        epd.display(img, mode)

        #img.save(path)
        return f"<h2>Bild wird Angezeigt!</h2>"

    return '''
    <h1>Bild hochladen</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file" required><br><br>
        <label><input type="radio" name="mode" value="fit" checked> Fit</label><br>
        <label><input type="radio" name="mode" value="fill"> Fill</label><br>
        <label><input type="radio" name="mode" value="stretch"> Stretch</label><br><br>
        <input type="submit" value="Hochladen">
    </form>
    '''
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
