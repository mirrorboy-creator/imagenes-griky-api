from flask import Flask, request, jsonify, send_file
import requests
import os
import json

app = Flask(__name__)

# === FUNCIONES ===

def buscar_en_wikimedia(titulo):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "generator": "search",
        "gsrsearch": titulo,
        "gsrlimit": 1,
        "iiprop": "url|extmetadata"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "query" in data:
        page = next(iter(data["query"]["pages"].values()))
        imageinfo = page.get("imageinfo", [{}])[0]
        image_url = imageinfo.get("url")
        metadata = imageinfo.get("extmetadata", {})

        autor = metadata.get("Artist", {}).get("value", "Desconocido")
        licencia = metadata.get("LicenseShortName", {}).get("value", "Desconocida")
        title = page.get("title", "").replace("File:", "")
        cita = f"Wikimedia Commons. (2025). *{title}* [Imagen]. {image_url}"

        return {
            "titulo": titulo,
            "url": image_url,
            "cita": cita,
            "fuente": "Wikimedia Commons",
            "autor": autor,
            "licencia": licencia
        }

    return None

def generar_con_ia(titulo):
    image_url = f"https://example.com/ia/{titulo.replace(' ', '_')}.jpg"  # Puedes integrar DALL·E aquí si quieres
    cita = f"Imagen generada por IA basada en el concepto académico '{titulo}'. (2025). [Imagen generada por IA]. DALL·E / OpenAI. {image_url}"
    return {
        "titulo": titulo,
        "url": image_url,
        "cita": cita,
        "fuente": "DALL·E / OpenAI",
        "autor": "IA",
        "licencia": "Uso académico permitido (imagen generada por IA)"
    }

# === ENDPOINT PRINCIPAL para GPT ===

@app.route("/imagenes", methods=["POST"])
def buscar_imagen_academica():
    data = request.get_json(silent=True) or {}
    titulo = data.get("titulo")

    if not titulo:
        return jsonify({"ok": False, "error": "El campo 'titulo' es obligatorio"}), 400

    resultado = buscar_en_wikimedia(titulo)
    if resultado:
        resultado["ok"] = True
        return jsonify(resultado)

    fallback = generar_con_ia(titulo)
    fallback["ok"] = True
    return jsonify(fallback)

# === SERVE SPEC PARA GPT ===

@app.route("/openapi.json")
def serve_openapi():
    with open("openapi.json") as f:
        spec = json.load(f)
    return jsonify(spec)

# === HEALTH CHECK ===

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
