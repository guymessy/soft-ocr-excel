
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import pandas as pd
from flask import Flask, request, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins="*")


@app.route("/upload", methods=["POST"])
def upload_pdf():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    doc = fitz.open(stream=file.read(), filetype="pdf")
    records = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang="eng")

        blocks = text.split("\n\n")
        for block in blocks:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            if len(lines) >= 5:
                records.append([" ".join(lines)])

    df = pd.DataFrame(records, columns=["OCR Row"])
    output_path = "output.xlsx"
    df.to_excel(output_path, index=False)

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
