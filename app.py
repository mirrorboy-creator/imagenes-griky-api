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
# ENDPOINT DE BÚSQUEDA DE IMÁGENES CON CITA APA
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

    # === INTENTO EN WIKIMEDIA COMMONS ===
    commons_api = f"https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "titles": f"File:{titulo.replace(' ', '_')}.svg",
        "iiprop": "url|extmetadata"
    }

    try:
        r = requests.get(commons_api, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
    except Exception:
        pages = {}

    for page_id, page_data in pages.items():
        if "imageinfo" in page_data:
            imageinfo = page_data["imageinfo"][0]
            url = imageinfo.get("url")
            metadata = imageinfo.get("extmetadata", {})

            autor = metadata.get("Artist", {}).get("value", "Desconocido")
            fuente = "Wikimedia Commons"
            licencia = metadata.get("LicenseShortName", {}).get("value", "Desconocida")
            cita = f"Wikimedia Commons. (2025). {titulo} [Imagen]. {url}"

            return jsonify({
                "ok": True,
                "titulo": titulo,
                "autor": autor,
                "fuente": fuente,
                "licencia": licencia,
                "url": url,
                "cita": cita
            })

    # === SI FALLA, USAR UNSPLASH ===
    fallback_url = f"https://source.unsplash.com/600x400/?{titulo.replace(' ', '+')}"
    cita = f"Unsplash. (s. f.). {titulo} [Imagen]. {fallback_url}"

    return jsonify({
        "ok": True,
        "titulo": titulo,
        "autor": "Desconocido",
        "fuente": "Unsplash",
        "licencia": "Libre uso educativo",
        "url": fallback_url,
        "cita": cita
    })


# =====================================================
# RENDER
# =====================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
