from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# ===============================
# FUNCIONES DE BÚSQUEDA EN FUENTES ABIERTAS
# ===============================

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

        for _, page in pages.items():
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


def buscar_en_europepmc(titulo):
    endpoint = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": f"{titulo} AND HAS_FT:Y",
        "format": "json",
        "resultType": "core",
        "pageSize": 1
    }

    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        results = data.get("resultList", {}).get("result", [])
        if not results:
            return None

        article = results[0]
        title = article.get("title", titulo)
        author = article.get("authorString", "Desconocido")
        year = article.get("pubYear", "s. f.")
        url = article.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url", "")

        return {
            "titulo": title,
            "url": url,
            "autor": author,
            "licencia": "Desconocida",
            "fuente": "EuropePMC",
            "año": year,
            "tipo": "Imagen de artículo científico",
            "ancho": 1000  # asumimos calidad decente
        }

    except Exception as e:
        print("Error buscando en EuropePMC:", e)
        return None


# ===============================
# GENERAR CON IA SI NO SE ENCUENTRA IMAGEN REAL
# ===============================

def generar_con_ia(titulo, fuente_base=None):
    url = f"https://example.com/ia/{titulo.replace(' ', '_')}.jpg"

    nota = f"**Figura 1.** Imagen generada por IA sobre {titulo.lower()}."
    referencia = f"OpenAI. (2025). *{titulo}* [Imagen generada por inteligencia artificial]. DALL·E. {url}"

    if fuente_base:
        nota += f" Basada en una imagen de fuente abierta: {fuente_base['titulo']}."
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

# ===============================
# ENDPOINT PRINCIPAL
# ===============================

@app.route("/imagenes", methods=["POST"])
def buscar_imagen_academica():
    data = request.get_json()
    titulo = data.get("titulo", "")

    # Paso 1: Wikimedia
    resultado = buscar_en_wikimedia(titulo)

    # Paso 2: EuropePMC si no se encuentra en Wikimedia
    if not resultado:
        resultado = buscar_en_europepmc(titulo)

    # Si se encuentra imagen válida y buena resolución
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

    # Si no hay imagen real válida, generar con IA
    imagen_ia = generar_con_ia(titulo, fuente_base=resultado if resultado else None)
    return jsonify(imagen_ia)


# ===============================
# SERVIR OPENAPI PARA CHATGPT
# ===============================

@app.route("/openapi.json")
def serve_openapi():
    try:
        with open("openapi.json") as f:
            spec = json.load(f)
        return jsonify(spec)
    except Exception as e:
        return jsonify({"error": f"No se pudo cargar openapi.json: {e}"}), 500


# ===============================
# SALUD DEL SERVIDOR
# ===============================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


# ===============================
# INICIAR
# ===============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
