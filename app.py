from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)


def buscar_en_wikimedia(titulo):
    endpoint = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "generator": "search",
        "gsrsearch": titulo,
        "gsrlimit": 1,
        "iiprop": "url|extmetadata|size"
    }

    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        if not pages:
            return None

        for page_id, page in pages.items():
            imageinfo = page.get("imageinfo", [])[0]
            metadata = imageinfo.get("extmetadata", {})
            licencia = metadata.get("LicenseShortName", {}).get("value", "Desconocida")
            autor = metadata.get("Artist", {}).get("value", "Desconocido")
            url = imageinfo.get("url", "")
            titulo_img = page.get("title", "").replace("File:", "").replace("_", " ")
            width = imageinfo.get("width", 0)

            return {
                "titulo": titulo_img,
                "url": url,
                "autor": autor,
                "licencia": licencia,
                "fuente": "Wikimedia Commons",
                "año": "s. f.",
                "tipo": "Diagrama",
                "ancho": width
            }

    except Exception as e:
        print("Error buscando en Wikimedia:", e)
        return None


def generar_con_ia(titulo, fuente_base=None):
    url = f"https://example.com/ia/{titulo.replace(' ', '_')}.jpg"

    nota = f"**Figura 1.** Imagen generada por IA sobre {titulo.lower()}."
    referencia = f"OpenAI. (2025). *{titulo}* [Imagen generada por inteligencia artificial]. DALL·E. {url}"

    if fuente_base:
        nota += f" Basada en una imagen con licencia abierta encontrada en {fuente_base['fuente']}."
        referencia += f"\n\nFuente base: {fuente_base['autor']}. ({fuente_base['año']}). *{fuente_base['titulo']}*. {fuente_base['fuente']}. {fuente_base['url']}"

    return {
        "titulo": titulo,
        "url": url,
        "autor": "OpenAI",
        "fuente": "DALL·E / OpenAI",
        "licencia": "Uso académico permitido (imagen generada por IA)",
        "nota": nota,
        "referencia": referencia,
        "markdown": f"![{titulo}]({url})",
        "generada_por_ia": True
    }


@app.route("/imagenes", methods=["POST"])
def buscar_imagen_academica():
    data = request.get_json()
    titulo = data.get("titulo", "")

    resultado = buscar_en_wikimedia(titulo)

    if resultado and resultado["ancho"] >= 700:
        figura = f"**Figura 1.** {resultado['titulo']}. Imagen académica con licencia {resultado['licencia']}."
        referencia = f"{resultado['autor']}. ({resultado['año']}). *{resultado['titulo']}* [{resultado['tipo']}]. {resultado['fuente']}. {resultado['url']}"
        return jsonify({
            "titulo": resultado["titulo"],
            "url": resultado["url"],
            "autor": resultado["autor"],
            "fuente": resultado["fuente"],
            "licencia": resultado["licencia"],
            "nota": figura,
            "referencia": referencia,
            "markdown": f"![{titulo}]({resultado['url']})",
            "generada_por_ia": False
        })

    # Si no se encuentra o es de baja calidad
    imagen_ia = generar_con_ia(titulo, fuente_base=resultado if resultado else None)
    return jsonify(imagen_ia)


@app.route("/openapi.json")
def serve_openapi():
    try:
        with open("openapi.json") as f:
            spec = json.load(f)
        return jsonify(spec)
    except Exception as e:
        return jsonify({"error": f"No se pudo cargar openapi.json: {e}"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
