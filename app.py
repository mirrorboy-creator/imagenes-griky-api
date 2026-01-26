from flask import Flask, request, jsonify, send_file
import requests
import os
import json

app = Flask(__name__)

# =========================
# ✅ Health check (Render)
# =========================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

# =========================
# === FUNCIONES IMÁGENES ===
# =========================
def buscar_en_wikimedia(titulo: str):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "generator": "search",
        "gsrsearch": titulo,
        "gsrlimit": 1,
        "iiprop": "url"
    }

    response = requests.get(url, params=params, timeout=15)
    if response.status_code != 200:
        return None

    data = response.json()

    if "query" in data and "pages" in data["query"]:
        page = next(iter(data["query"]["pages"].values()))
        if "imageinfo" not in page or not page["imageinfo"]:
            return None

        image_url = page["imageinfo"][0].get("url")
        if not image_url:
            return None

        title_file = page.get("title", "").replace("File:", "").strip() or "Imagen"

        # Nota: aquí estás poniendo 2025 fijo; si quieres lo hacemos dinámico luego.
        citation = f"Wikimedia Commons. (2025). *{title_file}* [Imagen]. {image_url}"

        return {
            "ok": True,
            "titulo": titulo,
            "url": image_url,
            "cita": citation,
            "fuente": "Wikimedia Commons",
            "autor": "Desconocido",
            "licencia": "CC BY-SA o Dominio público"
        }

    return None

def generar_con_ia(titulo: str):
    # Placeholder (tu lógica real de IA iría aquí)
    image_url = f"https://example.com/ia/{titulo.replace(' ', '_')}.jpg"
    citation = (
        f"Imagen generada por IA basada en el concepto académico '{titulo}'. (2025). "
        f"[Imagen generada por IA]. DALL·E / OpenAI. {image_url}"
    )
    return {
        "ok": True,
        "titulo": titulo,
        "url": image_url,
        "cita": citation,
        "fuente": "DALL·E / OpenAI",
        "autor": "IA",
        "licencia": "Uso académico permitido (imagen generada por IA)"
    }

# =========================
# ✅ Endpoint que el Gateway/GPT espera
# POST /images  { "title": "..."}  (o {"q":"..."})
# =========================
@app.route("/images", methods=["POST"])
def images():
    data = request.get_json(silent=True) or {}
    titulo = data.get("title") or data.get("q")

    if not titulo:
        return jsonify({"ok": False, "error": "Missing title"}), 400

    resultado = buscar_en_wikimedia(titulo)
    if resultado:
        return jsonify(resultado)

    return jsonify(generar_con_ia(titulo))

# =========================
# (Opcional) Mantener compatibilidad con tu endpoint viejo
# GET /buscar-imagen?titulo=...
# =========================
@app.route("/buscar-imagen", methods=["GET"])
def buscar_imagen():
    titulo = request.args.get("titulo")
    if not titulo:
        return jsonify({"ok": False, "error": "Falta el parámetro 'titulo'"}), 400

    resultado = buscar_en_wikimedia(titulo)
    if resultado:
        return jsonify(resultado)

    return jsonify(generar_con_ia(titulo))

# =========================
# ✅ Servir openapi.json (UNA sola vez, sin duplicar rutas)
# =========================
@app.route("/openapi.json", methods=["GET"])
def serve_openapi():
    # Si existe archivo local, lo sirve. Si no, devuelve error claro.
    if not os.path.exists("openapi.json"):
        return jsonify({"ok": False, "error": "openapi.json not found"}), 404
    return send_file("openapi.json", mimetype="application/json")

# =========================
# ✅ Render
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
