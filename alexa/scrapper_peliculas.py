#!/usr/bin/env python3
"""
scrapper_pelicula.py — Consulta información de una película usando TMDB API.

Uso:
    python scrapper_pelicula.py "Interstellar"
    python scrapper_pelicula.py "El Padrino" --campo nota
    python scrapper_pelicula.py "Matrix" --campo sinopsis

Campos disponibles: nota, votos, sinopsis, director, duracion, year, generos
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.parse

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE    = "https://api.themoviedb.org/3"
LANG         = "es-ES"

CAMPOS_VALIDOS = ["nota", "votos", "sinopsis", "director", "duracion", "year", "generos"]


def tmdb_get(endpoint, params=None):
    params = params or {}
    params["api_key"]  = TMDB_API_KEY
    params["language"] = LANG
    url = f"{TMDB_BASE}{endpoint}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=8) as resp:
        return json.loads(resp.read().decode())


def buscar_pelicula(nombre):
    data = tmdb_get("/search/movie", {"query": nombre})
    resultados = data.get("results", [])
    return resultados[0] if resultados else None


def info_completa(nombre):
    pelicula = buscar_pelicula(nombre)
    if not pelicula:
        return None

    detalle = tmdb_get(f"/movie/{pelicula['id']}", {"append_to_response": "credits"})

    director = "Desconocido"
    for persona in detalle.get("credits", {}).get("crew", []):
        if persona.get("job") == "Director":
            director = persona["name"]
            break

    duracion_min = detalle.get("runtime", 0)
    horas   = duracion_min // 60
    minutos = duracion_min % 60
    duracion_str = f"{horas}h {minutos}min" if horas else f"{minutos}min"

    return {
        "titulo":   detalle.get("title", nombre),
        "year":     (detalle.get("release_date") or "")[:4] or "Desconocido",
        "nota":     round(detalle.get("vote_average", 0), 1),
        "votos":    detalle.get("vote_count", 0),
        "sinopsis": detalle.get("overview", "No disponible."),
        "director": director,
        "duracion": duracion_str,
        "generos":  [g["name"] for g in detalle.get("genres", [])],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Consulta información de una película usando TMDB."
    )
    parser.add_argument("pelicula", help="Nombre de la película a consultar")
    parser.add_argument(
        "--campo", "-c",
        choices=CAMPOS_VALIDOS,
        help="Campo concreto a mostrar (si no se indica, muestra todo)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Devuelve la salida en formato JSON"
    )
    args = parser.parse_args()

    info = info_completa(args.pelicula)

    if info is None:
        print(f"no se encontró información para: '{args.pelicula}'")
        sys.exit(1)

    if args.campo:
        valor = info[args.campo]
        if args.json:
            print(json.dumps({args.campo: valor}, ensure_ascii=False, indent=2))
        else:
            if isinstance(valor, list):
                print(", ".join(valor))
            else:
                print(valor)
        return

    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return

    # Salida legible por defecto
    print(f"\n{'='*50}")
    print(f"  {info['titulo']} ({info['year']})")
    print(f"{'='*50}")
    print(f"  Director  : {info['director']}")
    print(f"  Géneros   : {', '.join(info['generos']) if info['generos'] else 'N/A'}")
    print(f"  Duración  : {info['duracion']}")
    print(f"  Nota      : {info['nota']} / 10")
    print(f"  Votos     : {info['votos']:,}")
    print(f"\n  Sinopsis  :\n  {info['sinopsis']}\n")


if __name__ == "__main__":
    main()