# =====================================================
# ENDPOINT DE IMÁGENES ACADÉMICAS
# =====================================================
@app.route("/imagenes", methods=["POST"])
def imagenes():

    data = request.get_json(silent=True) or {}
    query = data.get("q")

    if not query:
        return jsonify({
            "ok": False,
            "error": "El campo 'q' es obligatorio para buscar imágenes académicas"
        }), 400

    # Buscamos en Wikimedia Commons
    search_url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}+filetype:bitmap|drawing&srnamespace=6&srprop="

    try:
        search_response = requests.get(search_url, timeout=15)
        search_response.raise_for_status()
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": "No se pudo conectar con Wikimedia Commons"
        }), 502

    search_results = search_response.json().get("query", {}).get("search", [])

    if not search_results:
        return jsonify({
            "ok": False,
            "mensaje": "No se encontraron imágenes académicas open access"
        }), 404

    # Tomamos el primero
    image_title = search_results[0]["title"]  # Ej: File:Chromosome_structure.svg

    image_info_url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&titles={image_title}&iiprop=url|extmetadata"

    try:
        image_info_response = requests.get(image_info_url, timeout=15)
        image_info_response.raise_for_status()
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": "Error obteniendo detalles de la imagen"
        }), 502

    pages = image_info_response.json().get("query", {}).get("pages", {})
    image_data = next(iter(pages.values()))
    image_info = image_data.get("imageinfo", [{}])[0]

    url = image_info.get("url")
    metadata = image_info.get("extmetadata", {})

    titulo_original = metadata.get("ObjectName", {}).get("value") or query
    autor = metadata.get("Artist", {}).get("value", "Desconocido").replace("<", "").replace(">", "")
    licencia = metadata.get("LicenseShortName", {}).get("value", "Desconocida")
    anio = metadata.get("DateTimeOriginal", {}).get("value", "s.f.").split("-")[0]

    # Formato APA
    cita_apa = f"{autor}. ({anio}). *{titulo_original}* [Imagen]. Wikimedia Commons. {url}"
    nota_figura = f"Figura 1. {titulo_original}. Imagen extraída de Wikimedia Commons ({anio})."

    return jsonify({
        "ok": True,
        "titulo": titulo_original,
        "url": url,
        "autor": autor,
        "anio": anio,
        "licencia": licencia,
        "fuente": "Wikimedia Commons",
        "nota_figura": nota_figura,
        "cita_apa": cita_apa
    })
