from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# =====================================================
# HEALTH CHECK
# =====================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

# =====================================================
# NUEVO ENDPOINT DE IMÁGENES (POST)
# =====================================================
@app.route("/imagenes", methods=["POST"])
def imagenes():
    data = request.get_json(silent=True) or {}

    titulo = data.get("titulo")
    if not titulo:
        return jsonify({"ok": False, "error": "Falta el campo 'titulo'"}), 400

    # Simulamos una búsqueda sencilla con Bing Image Search o similar
    resultados = [
        {
            "titulo": titulo,
            "url": f"https://source.unsplash.com/600x400/?{titulo.replace(' ', '+')}",
            "fuente": "Unsplash"
        }
    ]

    return jsonify({
        "ok": True,
        "resultados": resultados
    })

# =====================================================
# MENSAJE SI ABRES /imagenes EN NAVEGADOR (GET)
# =====================================================
@app.route("/imagenes", methods=["GET"])
def imagenes_info():
    return jsonify({
        "ok": False,
        "mensaje": "Este endpoint solo acepta solicitudes POST con JSON. No se usa desde el navegador."
    }), 405

# =====================================================
# RENDER
# =====================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
