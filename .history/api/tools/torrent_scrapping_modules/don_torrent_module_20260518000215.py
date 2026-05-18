from playwright.sync_api import sync_playwright
from pprint import pprint
from langchain.tools import tool
from rich import print as rprint

base_url = "https://dontorrent.rocks/"


def search_torrent(movie_name : str) -> str:
    """
    Encuentra un listado de películas disponibles para descargar y sus respectivos links de descarga.
    """


    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(base_url)
        page.click('#Close_fa')
        page.fill('#query', movie_name)
        page.keyboard.press('Enter')
        page.wait_for_selector(".card-body")
        films = page.locator('.card-body>p>span').all()


        torrents = list()

        for film in films:
            try:
                torrents.append({
                    "name": film.inner_text().replace("\n", ""),
                    "link": f"{base_url}{film.locator('a').get_attribute('href')}"
                })
            except Exception as e:
                torrents.append({
                    "name": film.inner_text().replace("\n", ""),
                    "link": "No se ha encontrado un link de descarga para esta película"
                })


    return torrents
    

def get_torrent_from_link(link : str) -> str:
    """
    Ejecuta la descarga de un archivo .torrent a partir de un link obtenido en la función search_torrent.
    """

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(link)
        page.click('#Close_fa')
        download_button = page.locator('a.protected-download')

        with page.expect_download() as download_info:
            download_button.click()

        download = download_info.value
        download.save_as(f"../torrents/{download.suggested_filename}")

    return f"{download.suggested_filename} descargado correctamente"
    
if __name__ == "__main__":
    rprint(search_torrent("spiderman"))
    #get_torrent_from_link('https://dontorrent.racing/pelicula/10890/Spider-Man-Spiderman-Mastered-in-4K')
