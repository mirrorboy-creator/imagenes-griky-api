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
# ENDPOINT DE BÚSQUEDA DE IMÁGENES
# =====================================================
@app.route("/imagenes", methods=["POST"])
def buscar_imagen():
    data = request.get_json(silent=True) or {}
    titulo = data.get("titulo", "").strip()

    if not titulo:
        return jsonify({"ok": False, "error": "El campo 'titulo' es obligatorio"}), 400

    # ----------------------------
    # Consulta a Wikimedia Commons API (open access)
    # ----------------------------
    search_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": titulo,
        "gsrlimit": 1,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata"
    }

    try:
        r = requests.get(search_url, params=params, timeout=15)
        data = r.json()
    except Exception as e:
        return jsonify({"ok": False, "error": "Error al consultar Wikimedia Commons"}), 502

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return jsonify({"ok": False, "mensaje": "No se encontraron imágenes en acceso abierto"}), 404

    # Tomamos la primera imagen encontrada
    page = list(pages.values())[0]
    imageinfo = page.get("imageinfo", [])[0]

    image_url = imageinfo.get("url")
    metadata = imageinfo.get("extmetadata", {})

    autor = metadata.get("Artist", {}).get("value", "Autor desconocido")
    fuente = metadata.get("Credit", {}).get("value", "Wikimedia Commons")
    licencia = metadata.get("LicenseShortName", {}).get("value", "Licencia abierta")

    titulo_imagen = page.get("title", "Sin título")
    anio = metadata.get("DateTime", {}).get("value", "s.f.")

    # ----------------------------
    # Generar referencia APA
    # ----------------------------
    referencia = f"{autor}. ({anio}). *{titulo_imagen}*. {fuente}. {image_url}"

    leyenda = f"Figura 1. Imagen relacionada con: {titulo}. Adaptado de {autor}, {anio}."

    return jsonify({
        "ok": True,
        "titulo_busqueda": titulo,
        "imagen": image_url,
        "titulo_imagen": titulo_imagen,
        "autor": autor,
        "fuente": fuente,
        "licencia": licencia,
        "anio": anio,
        "referencia_APA": referencia,
        "leyenda_APA": leyenda
    })

# =====================================================
# RENDER
# =====================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
