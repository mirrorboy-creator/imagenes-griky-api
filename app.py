from flask import Flask, request, jsonify

app = Flask(__name__)

# =====================================================
# HEALTH CHECK (Render)
# =====================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

# =====================================================
# ENDPOINT PARA BÚSQUEDA DE IMÁGENES (placeholder)
# =====================================================
@app.route("/imagenes", methods=["POST"])
def imagenes():
    data = request.get_json(silent=True) or {}
    titulo = data.get("titulo")

    if not titulo:
        return jsonify({
            "ok": False,
            "error": "El campo 'titulo' es obligatorio"
        }), 400

    # Placeholder de respuesta
    return jsonify({
        "ok": True,
        "mensaje": f"Búsqueda de imagen para el título: {titulo}",
        "imagen": None  # Aquí se integrará la lógica real en el siguiente paso
    })

# =====================================================
# RENDER
# =====================================================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
