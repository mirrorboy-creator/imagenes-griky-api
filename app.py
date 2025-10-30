from flask import Flask, request, jsonify
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
        "iiprop": "url"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "query" in data:
        page = next(iter(data["query"]["pages"].values()))
        image_url = page["imageinfo"][0]["url"]
        title = page["title"].replace("File:", "")
        citation = f"Wikimedia Commons. (2025). *{title}* [Imagen]. {image_url}"
        return {
            "titulo": titulo,
            "url": image_url,
            "cita": citation,
            "fuente": "Wikimedia Commons",
            "autor": "Desconocido",
            "licencia": "CC BY-SA o Dominio público"
        }

    return None

def generar_con_ia(titulo):
    image_url = f"https://example.com/ia/{titulo.replace(' ', '_')}.jpg"
    citation = f"Imagen generada por IA basada en el concepto académico '{titulo}'. (2025). [Imagen generada por IA]. DALL·E / OpenAI. {image_url}"
    return {
        "titulo": titulo,
        "url": image_url,
        "cita": citation,
        "fuente": "DALL·E / OpenAI",
        "autor": "IA",
        "licencia": "Uso académico permitido (imagen generada por IA)"
    }

# === ENDPOINT PRINCIPAL ===

@app.route("/buscar-imagen", methods=["GET"])
def buscar_imagen():
    titulo = request.args.get("titulo")
    if not titulo:
        return jsonify({"error": "Falta el parámetro 'titulo'"}), 400

    resultado = buscar_en_wikimedia(titulo)
    if resultado:
        return jsonify(resultado)

    return jsonify(generar_con_ia(titulo))

# === SERVE openapi.json para el GPT ===

@app.route("/openapi.json")
def openapi_spec():
    with open("openapi.json") as f:
        spec = json.load(f)
    return jsonify(spec)

# === PARA RENDER ===

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
