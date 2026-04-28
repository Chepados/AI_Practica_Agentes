import requests
from bs4 import BeautifulSoup
from rich import print as rprint
from film_scrapper import search_movie

def get_movie_info(titulo):
    """Obtiene información de la primera película encontrada buscando en TMDB."""
    tmdb_resultados = search_movie(titulo)
    info = tmdb_resultados[0] if tmdb_resultados else None
    return {"titulo": titulo, "info_tmdb": info}

def get_cartelera_madrid():
    """
    Obtiene la cartelera de películas actuales en los cines de Madrid. 
    Cada película de la cartelera contiene también su información de TMDB.
    """
    url = "https://www.ecartelera.com/cines/0,30,1.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Hacemos una petición a la web de la cartelera
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error al acceder a eCartelera: {e}")
        return []
        
    # Vamos a la estructura donde están las películas
    soup = BeautifulSoup(response.text, "html.parser")
    peliculas_items = soup.select(".movies-showtimes-grid .pitem")

    # Extraemos los títulos
    titulos = []
    for peli in peliculas_items:
        titulo_tag = peli.select_one("p.title a")
        if titulo_tag:
            titulos.append(titulo_tag.get_text(strip=True))
    
    # Buscamos la info en TMDB secuencialmente
    lista_peliculas = []
    if titulos:
        for titulo in titulos:
            lista_peliculas.append(get_movie_info(titulo))
        
    return [p for p in lista_peliculas if p.get("info_tmdb") is not None]




def format_movie(movie: dict) -> str:
    """
    Formatea la información de una película para mostrarla en el mensaje que se manda por Telegram/Alexa.
    """
    info = movie.get("info_tmdb")

    # Guardamos la info de la peli
    title = info.get("title")
    overview = info.get("overview") or "Sin sinopsis disponible."
    release_date = info.get("release_date") or "Fecha desconocida"
    vote_average = info.get("vote_average", None)
    vote_count = info.get("vote_count", 0)

    # Formateamos la nota.
    rating_text = (
        f"{vote_average:.1f}/10"
        if isinstance(vote_average, (int, float))
        else "Sin nota"
    )

    # Acortamos la sinopsis.
    max_overview_len = 280
    if len(overview) > max_overview_len:
        overview = overview[:max_overview_len].rstrip() + "..."

    return (
        f"Título: {title}\n"
        f"Estreno: {release_date}\n"
        f"Nota: {rating_text} ({vote_count} votos)\n"
        f"Sinopsis: {overview}"
    )
def format_cartelera_message(movies, max_movies: int = 10) -> str:
    """
    Formatea la cartelera completa para mostrarla como string en el mensaje que se manda por Telegram/Alexa.
    Ordena las películas por popularidad (número de votos) y muestra solo las top `max_movies` para no saturar el mensaje.
    """
    if not movies:
        return "No he encontrado películas en la cartelera de Madrid."

    # Ordenamos películas por popularidad y elegimos la cantidad que queramos.
    movies.sort(key=lambda x: x["info_tmdb"]["vote_count"], reverse=True)
    selected_movies = movies[:max_movies]


    if len(movies) > max_movies:
        footer = f"\n\nMostrando {max_movies} de {len(movies)} películas encontradas."
    else:
        footer = ""

    return (
        "🎟️ Cartelera de Madrid por popularidad\n\n" + \
        "\n\n━━━━━━━━━━━━━━\n\n".join(format_movie(movie) for movie in selected_movies) + \
        footer
    )


if __name__ == "__main__":
    import time
    start = time.time()
    
    lista_peliculas_json = get_cartelera_madrid()
    rprint(lista_peliculas_json)
    
    print(f"\n✨ Scraping completado en {time.time() - start:.2f} segundos.")

    rprint(format_cartelera_message(lista_peliculas_json, 20))
