from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "API de imágenes académicas Griky está activa."

@app.route('/buscar-imagen', methods=['GET'])
def buscar_imagen():
    titulo = request.args.get('titulo', '').lower()

    # 🔍 Simulación de búsqueda de imagen
    imagen = {
        "titulo": titulo,
        "url": f"https://example.com/{titulo.replace(' ', '_')}.jpg",
        "cita": f"OpenAI. (2025). {titulo.title()}. https://example.com/{titulo.replace(' ', '_')}.jpg"
    }

    return jsonify(imagen)

# ✅ Esta parte es FUNDAMENTAL para que funcione en Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render te da el puerto
    app.run(host="0.0.0.0", port=port)

