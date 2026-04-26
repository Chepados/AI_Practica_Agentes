import requests
from bs4 import BeautifulSoup
from pprint import pprint
from langchain.tools import tool
import os

def search_torrent_public_domain(movie_name: str) -> list[dict] | str:
    """
    Busca una película en publicdomaintorrents.info y devuelve un listado de resultados con sus respectivos links.
    """
    # Esta es una url con todas las películas de dominio público en la web.
    url = "https://www.publicdomaintorrents.info/nshowcat.html?category=ALL"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        return f"Error al conectar con la página: {e}"
    # Convertimos el nombre de la película a minúsculas para compararlo con los links de la web.
    movie_searched = movie_name.lower()

    soup = BeautifulSoup(response.text, "html.parser")
    # Encontramos todos los links a películas, que tienen este formato.
    torrents = []
    movie_links = soup.select('td > a[href^="nshowmovie.html?movieid="]')
    for link in movie_links:
        title = link.get_text(strip=True)
        if movie_searched in title.lower():
            # Si la encontramos creamos el link absoluto a la película para la siguiente fase.
            try:
                href = link.get('href')
                absolute_link = f"https://www.publicdomaintorrents.info/{href}"
                torrents.append({
                    "name": title,
                    "link": absolute_link
                })
            except Exception as e:
                torrents.append({
                    "name": title,
                    "link": "No se ha encontrado un link de descarga para esta película"
                })

    if not torrents:
        return []

    return torrents
    

def get_torrent_from_link_public_domain(link_data: dict[str, str]) -> str:
    """
    Descarga el archivo .torrent a partir de un link a la página de la película en publicdomaintorrents.info.
    """
    try:
        response = requests.get(link_data["link"], timeout=15)
        response.raise_for_status()
    except Exception as e:
        return f"Error al acceder al link de la película: {e}"
        
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Buscamos el link directo al archivo torrent (.avi suele ser de mejor calidad)
    # Ejemplo link descarga: <a href="http://www.publicdomaintorrents.com/bt/btdownload.php?type=torrent&amp;file=The_Eagle.avi.torrent">Click for Divx 716MB AVI</a>
    # Los enlaces a descargas son tipo "a" con href.
    torrent_links = soup.find_all("a", href=True)
    
    download_url = None
    
    for a in torrent_links:
        href = a['href']
        # Todos los links a descargas tienen "btdownload.php" y "torrent" en su href.
        if "btdownload.php" in href and "torrent" in href:
            # Preferimos la versión en .avi si está disponible
            if ".avi." in href:
                download_url = href
                break
            if not download_url:
                download_url = href
                
    if not download_url:
        return "No se ha encontrado un archivo torrent válido en la página."


    # Descargamos el archivo torrent
    try:
        torrent_response = requests.get(download_url, timeout=15)
        torrent_response.raise_for_status()
        
        # Extraemos el nombre del archivo de la URL
        filename = download_url.split("file=")[-1] if "file=" in download_url else f"{link_data.get('name', 'movie')}.torrent"
        
        save_dir = "torrents"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        filepath = os.path.join(save_dir, filename)
        with open(filepath, "wb") as f:
            f.write(torrent_response.content)
            
        return f"{filename} descargado correctamente en la carpeta torrents."
    except Exception as e:
        return f"Error al descargar el archivo torrent: {e}"
