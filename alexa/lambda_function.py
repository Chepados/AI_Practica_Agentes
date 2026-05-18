"""
lambda_function.py — Alexa Skill "Cine Info"
Usa la API de TMDB para obtener información de películas de forma rápida
Requiere la TMDB_API_KEY en la configuracion
"""

import json
import os
import urllib.request
import urllib.parse

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE    = "https://api.themoviedb.org/3"
LANG         = "es-ES"

from scrapper_peliculas import info_completa
# info = info_completa(nombre)


def tmdb_get(endpoint, params=None):
    """Hace una petición GET a la API de TMDB y devuelve el JSON."""
    params = params or {}
    params["api_key"]  = TMDB_API_KEY
    params["language"] = LANG
    url = f"{TMDB_BASE}{endpoint}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read().decode())

def buscar_pelicula(nombre):
    """Devuelve el primer resultado de búsqueda o None."""
    data = tmdb_get("/search/movie", {"query": nombre})
    resultados = data.get("results", [])
    if not resultados:
        return None
    return resultados[0]


def detalle_pelicula(movie_id):
    """Devuelve los detalles completos de una película."""
    return tmdb_get(f"/movie/{movie_id}", {"append_to_response": "credits"})


def info_completa(nombre):
    """Devuelve un dict con toda la info o None si no se encuentra."""
    pelicula = buscar_pelicula(nombre)
    if not pelicula:
        return None
    detalle = detalle_pelicula(pelicula["id"])

    # Director
    director = "desconocido"
    crew = detalle.get("credits", {}).get("crew", [])
    for persona in crew:
        if persona.get("job") == "Director":
            director = persona["name"]
            break

    # Géneros
    generos = [g["name"] for g in detalle.get("genres", [])]

    # Duración
    duracion = detalle.get("runtime", 0)

    return {
        "titulo":    detalle.get("title", nombre),
        "year":      (detalle.get("release_date") or "")[:4] or "desconocido",
        "nota":      round(detalle.get("vote_average", 0), 1),
        "votos":     detalle.get("vote_count", 0),
        "sinopsis":  detalle.get("overview", "No disponible."),
        "director":  director,
        "duracion":  duracion,
        "generos":   generos,
    }


# Helpers de respuesta Alexa
def build_response(speech, reprompt=None, should_end=True, card_title=None, card_content=None):
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": speech
            },
            "shouldEndSession": should_end
        }
    }
    if reprompt:
        response["response"]["reprompt"] = {
            "outputSpeech": {"type": "PlainText", "text": reprompt}
        }
    if card_title:
        response["response"]["card"] = {
            "type": "Simple",
            "title": card_title,
            "content": card_content or speech
        }
    return response


def hablar_pelicula_no_encontrada(nombre):
    return build_response(
        f"Lo siento, no he encontrado información sobre {nombre}. "
        "¿Puedes repetir el título de la película?"
    )


# handlers

def handle_launch():
    speech = (
        "Bienvenido a tu asesor de películas. Puedes preguntarme sobre la nota, sinopsis, "
        "director, duración o año de estreno de cualquier película. ¿Sobre qué película quieres saber?"
    )
    return build_response(
        speech,
        reprompt="¿De qué película quieres saber algo?",
        should_end=False
    )


def handle_nota(slots):
    nombre = slots.get("pelicula", {}).get("value", "")

    if not nombre:
        return build_response(
            "¿De qué película quieres saber la nota?",
            should_end=False
        )

    info = info_completa(nombre)

    if not info:
        return hablar_pelicula_no_encontrada(nombre)

    speech = (
        f"{info['titulo']} tiene una nota de {info['nota']} sobre 10, "
        f"basada en {info['votos']:,} votos."
    )

    return build_response(
        speech,
        card_title=info["titulo"],
        card_content=speech
    )


def handle_sinopsis(slots):
    nombre = slots.get("pelicula", {}).get("value", "")

    if not nombre:
        return build_response(
            "¿De qué película quieres la sinopsis?",
            should_end=False
        )

    info = info_completa(nombre)

    if not info:
        return hablar_pelicula_no_encontrada(nombre)

    speech = f"{info['titulo']}: {info['sinopsis']}"

    return build_response(
        speech,
        card_title=info["titulo"],
        card_content=speech
    )


def handle_year(slots):
    nombre = slots.get("pelicula", {}).get("value", "")

    if not nombre:
        return build_response(
            "¿De qué película quieres saber el año de estreno?",
            should_end=False
        )

    info = info_completa(nombre)

    if not info:
        return hablar_pelicula_no_encontrada(nombre)

    speech = f"{info['titulo']} se estrenó en el año {info['year']}."

    return build_response(
        speech,
        card_title=info["titulo"],
        card_content=speech
    )


def handle_votos(slots):
    nombre = slots.get("pelicula", {}).get("value", "")

    if not nombre:
        return build_response(
            "¿De qué película quieres saber los votos?",
            should_end=False
        )

    info = info_completa(nombre)

    if not info:
        return hablar_pelicula_no_encontrada(nombre)

    speech = f"{info['titulo']} tiene {info['votos']:,} valoraciones en The Movie Database."

    return build_response(
        speech,
        card_title=info["titulo"],
        card_content=speech
    )


def handle_director(slots):
    nombre = slots.get("pelicula", {}).get("value", "")

    if not nombre:
        return build_response(
            "¿De qué película quieres saber el director?",
            should_end=False
        )

    info = info_completa(nombre)

    if not info:
        return hablar_pelicula_no_encontrada(nombre)

    speech = f"{info['titulo']} fue dirigida por {info['director']}."

    return build_response(
        speech,
        card_title=info["titulo"],
        card_content=speech
    )


def handle_duracion(slots):
    nombre = slots.get("pelicula", {}).get("value", "")

    if not nombre:
        return build_response(
            "¿De qué película quieres saber la duración?",
            should_end=False
        )

    info = info_completa(nombre)

    if not info:
        return hablar_pelicula_no_encontrada(nombre)

    speech = f"{info['titulo']} dura {info['duracion']}."

    return build_response(
        speech,
        card_title=info["titulo"],
        card_content=speech
    )


def handle_info_completa(slots):
    nombre = slots.get("pelicula", {}).get("value", "")

    if not nombre:
        return build_response(
            "¿De qué película quieres información?",
            should_end=False
        )

    info = info_completa(nombre)

    if not info:
        return hablar_pelicula_no_encontrada(nombre)

    generos_str = ", ".join(info["generos"]) if info["generos"] else "varios géneros"

    speech = (
        f"{info['titulo']}, estrenada en {info['year']}, "
        f"fue dirigida por {info['director']}. "
        f"Es una película de {generos_str}, dura {info['duracion']} "
        f"y tiene una nota de {info['nota']} sobre 10."
    )

    return build_response(
        speech,
        card_title=info["titulo"],
        card_content=speech
    )


def handle_help():
    speech = (
        "Puedo darte información sobre cualquier película. Por ejemplo, puedes decirme: "
        "¿cuál es la nota de Interstellar?, ¿de qué trata El Padrino?, "
        "¿cuándo se estrenó Titanic?, o ¿quién dirigió Matrix?"
    )

    return build_response(
        speech,
        reprompt="¿Sobre qué película quieres saber?",
        should_end=False
    )


def handle_cancel_stop():
    return build_response("¡Hasta luego! Espero haberte ayudado.")


def handle_fallback():
    speech = (
        "No he entendido bien. Puedes preguntarme por la nota, sinopsis, director, "
        "duración o año de una película."
    )

    return build_response(
        speech,
        reprompt="¿Sobre qué película quieres saber?",
        should_end=False
    )


def handle_cancel_stop():
    return build_response("¡Hasta luego! Espero haberte ayudado.")


def handle_fallback():
    speech = (
        "No he entendido bien. Puedes preguntarme por la nota, sinopsis, director, "
        "duración o año de una película. ¿Qué quieres saber?"
    )
    return build_response(speech, reprompt="¿Sobre qué película quieres saber?", should_end=False)


# los entry points

def lambda_handler(event, context):
    """Punto de entrada de la Lambda de AWS."""
    request_type = event["request"]["type"]

    # LaunchRequest: el usuario abre la skill sin decir nada
    if request_type == "LaunchRequest":
        return handle_launch()

    # SessionEndedRequest
    if request_type == "SessionEndedRequest":
        return build_response("")

    # IntentRequest
    if request_type == "IntentRequest":
        intent_name = event["request"]["intent"]["name"]
        slots = event["request"]["intent"].get("slots", {})

        handlers = {
            "NotaPeliculaIntent":       handle_nota,
            "SinopsisPeliculaIntent":   handle_sinopsis,
            "YearPeliculaIntent":       handle_year,
            "VotosPeliculaIntent":      handle_votos,
            "DirectorPeliculaIntent":   handle_director,
            "DuracionPeliculaIntent":   handle_duracion,
            "InfoCompletaIntent":       handle_info_completa,
            "AMAZON.HelpIntent":        lambda s: handle_help(),
            "AMAZON.CancelIntent":      lambda s: handle_cancel_stop(),
            "AMAZON.StopIntent":        lambda s: handle_cancel_stop(),
            "AMAZON.FallbackIntent":    lambda s: handle_fallback(),
            "AMAZON.NavigateHomeIntent":lambda s: handle_launch(),
        }

        handler = handlers.get(intent_name)
        if handler:
            return handler(slots)

        return build_response("No sé cómo responder a eso. Prueba preguntando por una película.")

    return build_response("Ha ocurrido un error inesperado.")
