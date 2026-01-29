from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# =====================================================
# HEALTH CHECK (Render)
# =====================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

# =====================================================
# ENDPOINT DE BÚSQUEDA DE IMÁGENES CON FALLBACK
# =====================================================
@app.route("/imagenes", methods=["POST"])
def buscar_imagen_academica():
    data = request.get_json(silent=True) or {}
    titulo = data.get("titulo")

    if not titulo:
        return jsonify({
            "ok": False,
            "error": "El campo 'titulo' es obligatorio"
        }), 400

    # === CONSULTA A WIKIMEDIA COMMONS ===
    commons_api = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&titles=File:{titulo.replace(' ', '_')}.svg&iiprop=url|extmetadata"

    try:
        response = requests.get(commons_api, timeout=15)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
    except Exception:
        pages = {}

    for page_id, page_data in pages.items():
        if "imageinfo" in page_data:
            imageinfo = page_data["imageinfo"][0]
            metadata = imageinfo.get("extmetadata", {})
            url = imageinfo.get("url")
            licencia = metadata.get("LicenseShortName", {}).get("value", "Desconocida")
            autor = metadata.get("Artist", {}).get("value", "Desconocido")

            return jsonify({
                "ok": True,
                "titulo": titulo,
                "url": url,
                "autor": autor,
                "fuente": "Wikimedia Commons",
                "licencia": licencia,
                "cita": f"Wikimedia Commons. (2025). {titulo} [Imagen]. {url}"
            })

    # === FALLBACK A UNSPLASH ===
    fallback_url = f"https://source.unsplash.com/600x400/?{titulo.replace(' ', '+')}"

    return jsonify({
        "ok": True,
        "titulo": titulo,
        "url": fallback_url,
        "autor": "Desconocido",
        "fuente": "Unsplash",
        "licencia": "Libre uso educativo",
        "cita": f"Unsplash. (s. f.). {titulo} [Imagen]. {fallback_url}"
    })


# =====================================================
# RENDER
# =====================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
