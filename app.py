
from flask import Flask, request, jsonify
import os
import fitz  # PyMuPDF
import openai
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

# PDF klasöründeki tüm PDF içeriklerini yükle
pdf_texts = []
pdf_folder = "pdf"
for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        with fitz.open(os.path.join(pdf_folder, filename)) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            pdf_texts.append(text)

pdf_icerigi = "\n\n".join(pdf_texts)[:15000]  # max context için sınırlıyoruz

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    soru = data.get("question", "")

    prompt = f"Sadece aşağıdaki PDF içeriğine göre cevap ver:\n\n{pdf_icerigi}\n\nSoru: {soru}\nCevap:"
    
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen PDF belgeleri konusunda uzman bir yardımcı botsun."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        cevap = completion.choices[0].message["content"]
        return jsonify({"answer": cevap.strip()})
    except Exception as e:
        return jsonify({"answer": f"Hata: {str(e)}"})
