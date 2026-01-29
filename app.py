from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# ================================================================
# FUNCIONES AUXILIARES
# ================================================================

def buscar_en_wikimedia(titulo):
    """
    Busca una imagen en Wikimedia Commons con licencia abierta
    """
    endpoint = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "generator": "search",
        "gsrsearch": titulo,
        "gsrlimit": 1,
        "iiprop": "url|extmetadata"
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

            return {
                "titulo": titulo_img,
                "url": url,
                "autor": autor,
                "licencia": licencia,
                "fuente": "Wikimedia Commons",
                "año": "s.f.",  # Si no se encuentra, usa sin fecha
                "tipo": "Diagrama"
            }

    except Exception as e:
        print("Error buscando en Wikimedia:", e)
        return None

def generar_con_ia(titulo):
    """
    Simula generación de imagen por IA con referencia académica
    """
    url = f"https://example.com/ia/{titulo.replace(' ', '_')}.jpg"
    return {
        "titulo": titulo,
        "url": url,
        "autor": "OpenAI",
        "fuente": "DALL·E / OpenAI",
        "licencia": "Uso académico permitido (IA)",
        "referencia": f"OpenAI. (2025). *{titulo}* [Imagen generada por inteligencia artificial]. DALL·E. {url}",
        "nota": f"**Figura 1.** Imagen generada por IA sobre {titulo.lower()}.",
        "markdown": f"![{titulo}]({url})"
    }

# ================================================================
# RUTA PRINCIPAL QUE USA TU GPT
# ================================================================

@app.route("/imagenes", methods=["POST"])
def buscar_imagen_academica():
    data = request.get_json()
    titulo = data.get("titulo", "")

    resultado = buscar_en_wikimedia(titulo)

    if resultado:
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

    # Si no se encontró una imagen real adecuada:
    fallback = generar_con_ia(titulo)

    return jsonify({
        "titulo": fallback["titulo"],
        "url": fallback["url"],
        "autor": fallback["autor"],
        "fuente": fallback["fuente"],
        "licencia": fallback["licencia"],
        "nota": fallback["nota"],
        "referencia": fallback["referencia"],
        "markdown": fallback["markdown"],
        "generada_por_ia": True
    })


# ================================================================
# SERVIR /openapi.json PARA CHATGPT ACTIONS
# ================================================================

@app.route("/openapi.json")
def serve_openapi():
    try:
        with open("openapi.json") as f:
            spec = json.load(f)
        return jsonify(spec)
    except Exception as e:
        return jsonify({"error": f"No se pudo cargar openapi.json: {e}"}), 500


# ================================================================
# HEALTH CHECK
# ================================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


# ================================================================
# INICIAR SERVIDOR
# ================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
