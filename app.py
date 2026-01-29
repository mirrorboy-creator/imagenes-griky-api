from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# =============================
# 1. WIKIMEDIA COMMONS
# =============================

def buscar_en_wikimedia(titulo):
    try:
        response = requests.get("https://commons.wikimedia.org/w/api.php", params={
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "generator": "search",
            "gsrsearch": titulo,
            "gsrlimit": 1,
            "iiprop": "url|extmetadata|size"
        })

        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        if not pages:
            return None

        for _, page in pages.items():
            img = page.get("imageinfo", [])[0]
            meta = img.get("extmetadata", {})
            return {
                "titulo": page.get("title", "").replace("File:", "").replace("_", " "),
                "url": img.get("url", ""),
                "autor": meta.get("Artist", {}).get("value", "Desconocido"),
                "licencia": meta.get("LicenseShortName", {}).get("value", "Desconocida"),
                "fuente": "Wikimedia Commons",
                "año": "s. f.",
                "tipo": "Diagrama",
                "ancho": img.get("width", 0)
            }
    except Exception as e:
        print("Error en Wikimedia:", e)
        return None

# =============================
# 2. EUROPEPMC
# =============================

def buscar_en_europepmc(titulo):
    try:
        response = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params={
            "query": f"{titulo} AND HAS_FT:Y",
            "format": "json",
            "resultType": "core",
            "pageSize": 1
        })
        data = response.json()
        res = data.get("resultList", {}).get("result", [])
        if not res:
            return None
        art = res[0]
        return {
            "titulo": art.get("title", titulo),
            "url": art.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url", ""),
            "autor": art.get("authorString", "Desconocido"),
            "licencia": "Desconocida",
            "fuente": "EuropePMC",
            "año": art.get("pubYear", "s. f."),
            "tipo": "Imagen de artículo científico",
            "ancho": 1000
        }
    except Exception as e:
        print("Error en EuropePMC:", e)
        return None

# =============================
# 3. OPENVERSE
# =============================

def buscar_en_openverse(titulo):
    try:
        response = requests.get("https://api.openverse.engineering/v1/images", params={
            "q": titulo,
            "license_type": "commercial",
            "license": "cc0,by",
            "page_size": 1
        })
        data = response.json()
        result = data.get("results", [])
        if not result:
            return None
        img = result[0]
        return {
            "titulo": img.get("title", titulo),
            "url": img.get("url", ""),
            "autor": img.get("creator", "Desconocido"),
            "licencia": img.get("license", "Desconocida").upper(),
            "fuente": "Openverse",
            "año": "s. f.",
            "tipo": "Imagen ilustrativa",
            "ancho": 1000
        }
    except Exception as e:
        print("Error en Openverse:", e)
        return None

# =============================
# 4. PIXABAY
# =============================

def buscar_en_pixabay(titulo):
    try:
        response = requests.get("https://pixabay.com/api/", params={
            "key": "TU_API_KEY_PIXABAY",  # ← Inserta tu API KEY real aquí
            "q": titulo,
            "image_type": "illustration",
            "per_page": 1
        })
        data = response.json()
        hits = data.get("hits", [])
        if not hits:
            return None
        img = hits[0]
        return {
            "titulo": img.get("tags", titulo),
            "url": img.get("largeImageURL", ""),
            "autor": img.get("user", "Pixabay"),
            "licencia": "CC0",
            "fuente": "Pixabay",
            "año": "s. f.",
            "tipo": "Ilustración libre",
            "ancho": img.get("imageWidth", 0)
        }
    except Exception as e:
        print("Error en Pixabay:", e)
        return None

# =============================
# 5. GENERACIÓN CON IA
# =============================

def generar_con_ia(titulo, fuente_base=None):
    url = f"https://example.com/ia/{titulo.replace(' ', '_')}.jpg"
    nota = f"**Figura 1.** Imagen generada por IA sobre {titulo.lower()}."
    referencia = f"OpenAI. (2025). *{titulo}* [Imagen generada por inteligencia artificial]. DALL·E. {url}"

    if fuente_base:
        nota += f" Basada en contenido abierto consultado en {fuente_base['fuente']}."
        referencia += f"\n\nFuente base: {fuente_base['autor']}. ({fuente_base['año']}). *{fuente_base['titulo']}*. {fuente_base['fuente']}. {fuente_base['url']}"

    return {
        "titulo": titulo,
        "url": url,
        "autor": "OpenAI",
        "fuente": "DALL·E / OpenAI",
        "licencia": "Uso académico permitido (IA)",
        "nota": nota,
        "referencia": referencia,
        "markdown": f"![{titulo}]({url})",
        "generada_por_ia": True
    }

# =============================
# ENDPOINT PRINCIPAL
# =============================

@app.route("/imagenes", methods=["POST"])
def buscar_imagen_academica():
    data = request.get_json()
    titulo = data.get("titulo", "")

    fuentes = [
        buscar_en_wikimedia,
        buscar_en_europepmc,
        buscar_en_openverse,
        buscar_en_pixabay
    ]

    resultado = None
    for fuente in fuentes:
        resultado = fuente(titulo)
        if resultado and resultado["ancho"] >= 700:
            break

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

    return jsonify(generar_con_ia(titulo, fuente_base=resultado if resultado else None))

# =============================
# SALUD Y OPENAPI
# =============================

@app.route("/openapi.json")
def serve_openapi():
    try:
        with open("openapi.json") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

# =============================
# ARRANQUE
# =============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
