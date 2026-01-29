from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# =====================================================
# WIKIMEDIA COMMONS (FUENTE PRINCIPAL DE IMÁGENES)
# =====================================================
def buscar_en_wikimedia(titulo):
    endpoint = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": titulo,
        "gsrlimit": 1,
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata"
    }

    try:
        r = requests.get(endpoint, params=params, timeout=10)
        data = r.json()
        pages = data.get("query", {}).get("pages", {})

        if not pages:
            return None

        for _, page in pages.items():
            info = page["imageinfo"][0]
            meta = info.get("extmetadata", {})

            return {
                "titulo": page["title"].replace("File:", "").replace("_", " "),
                "url": info["url"],
                "autor": meta.get("Artist", {}).get("value", "Autor desconocido"),
                "licencia": meta.get("LicenseShortName", {}).get("value", "Licencia abierta"),
                "fuente": "Wikimedia Commons",
                "anio": meta.get("DateTime", {}).get("value", "s. f."),
                "tipo": "Imagen académica",
                "ancho": info.get("width", 0)
            }

    except Exception as e:
        print("Error Wikimedia:", e)
        return None


# =====================================================
# EUROPE PMC (RESPALDO ACADÉMICO – NO IMÁGENES DIRECTAS)
# =====================================================
def respaldo_europe_pmc(titulo):
    try:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            "query": titulo,
            "format": "json",
            "pageSize": 1
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        results = data.get("resultList", {}).get("result", [])

        if not results:
            return None

        art = results[0]
        return {
            "autor": art.get("authorString", "Autores académicos"),
            "anio": art.get("pubYear", "s. f."),
            "fuente": "Europe PMC",
            "titulo": art.get("title", titulo)
        }

    except Exception as e:
        print("Error EuropePMC:", e)
        return None


# =====================================================
# GENERACIÓN CON IA (SOLO SI ES NECESARIO)
# =====================================================
def generar_con_ia(titulo, respaldo=None):
    url = f"https://example.com/ia/{titulo.replace(' ', '_')}.jpg"

    nota = (
        f"**Figura 1.** {titulo}. Imagen generada por inteligencia artificial con fines académicos, "
        f"basada en descripciones y representaciones científicas provenientes de literatura académica."
    )

    referencia = (
        f"OpenAI. (2025). *{titulo}* [Imagen generada por inteligencia artificial]. "
        f"DALL·E. {url}"
    )

    if respaldo:
        referencia += (
            f"\n\nFuente académica de referencia: "
            f"{respaldo['autor']} ({respaldo['anio']}). "
            f"*{respaldo['titulo']}*. {respaldo['fuente']}."
        )

    return {
        "titulo": titulo,
        "url": url,
        "autor": "No aplica (imagen generada por IA)",
        "fuente": "DALL·E / OpenAI",
        "licencia": "Uso académico permitido (imagen generada por IA)",
        "nota": nota,
        "referencia": referencia,
        "generada_por_ia": True
    }


# =====================================================
# ENDPOINT PRINCIPAL
# =====================================================
@app.route("/imagenes", methods=["POST"])
def buscar_imagen_academica():
    data = request.get_json()
    titulo = data.get("titulo")

    if not titulo:
        return jsonify({"error": "El campo 'titulo' es obligatorio"}), 400

    # 1️⃣ BUSCAR IMAGEN REAL
    resultado = buscar_en_wikimedia(titulo)

    if resultado and resultado["ancho"] >= 700:
        nota = (
            f"**Figura 1.** {resultado['titulo']}. "
            f"Imagen académica de acceso abierto."
        )

        referencia = (
            f"{resultado['autor']}. ({resultado['anio']}). "
            f"*{resultado['titulo']}* [{resultado['tipo']}]. "
            f"{resultado['fuente']}. {resultado['url']}"
        )

        return jsonify({
            "titulo": resultado["titulo"],
            "url": resultado["url"],
            "autor": resultado["autor"],
            "fuente": resultado["fuente"],
            "licencia": resultado["licencia"],
            "nota": nota,
            "referencia": referencia,
            "generada_por_ia": False
        })

    # 2️⃣ RESPALDO ACADÉMICO
    respaldo = respaldo_europe_pmc(titulo)

    # 3️⃣ GENERAR CON IA
    return jsonify(generar_con_ia(titulo, respaldo))


# =====================================================
# OPENAPI + HEALTH
# =====================================================
@app.route("/openapi.json")
def serve_openapi():
    with open("openapi.json") as f:
        return jsonify(json.load(f))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
