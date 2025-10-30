from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def generar_referencia_apa(titulo, autor, anio, fuente, url):
    return {
        "note_apa": f"Figura 1. {titulo}. Adaptado de {autor}, {anio}.",
        "reference_apa": f"{autor}. ({anio}). *{titulo}*. {fuente}. {url}"
    }

@app.route("/buscar-imagen", methods=["GET"])
def buscar_imagen():
    titulo = request.args.get("titulo")
    if not titulo:
        return jsonify({"error": "Falta el parámetro 'titulo'."}), 400

    response = requests.get("https://commons.wikimedia.org/w/api.php", {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": titulo,
        "gsrlimit": 1,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata"
    })

    data = response.json()

    try:
        page = list(data['query']['pages'].values())[0]
        imageinfo = page['imageinfo'][0]
        metadata = imageinfo['extmetadata']

        image_url = imageinfo['url']
        title = metadata.get('ObjectName', {}).get('value', titulo)
        author = metadata.get('Artist', {}).get('value', 'Desconocido')
        license = metadata.get('LicenseShortName', {}).get('value', 'Desconocido')
        year = metadata.get('DateTimeOriginal', {}).get('value', 's.f.')[:4]
        source = "Wikimedia Commons"

        citas = generar_referencia_apa(title, author, year, source, image_url)

        return jsonify({
            "status": "found",
            "image_url": image_url,
            "title": title,
            "author": author,
            "license": license,
            "source": source,
            "note_apa": citas['note_apa'],
            "reference_apa": citas['reference_apa']
        })

    except Exception as e:
        return jsonify({
            "status": "not_found",
            "message": f"No se encontró una imagen académica con ese título.",
            "error": str(e)
        }), 404

if __name__ == "__main__":
    app.run(debug=True)
