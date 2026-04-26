import os
import importlib
from rich import print as rprint




def get_available_modules() -> list[str]:
    """
    Devuelve una lista de los módulos de scrapping disponibles en la carpeta torrent_scrapping_modules.
    """

    lista = os.listdir("./tools/torrent_scrapping_modules")
    
    lista = [module for module in lista if module.endswith(".py") and module != "__init__.py"]

    return lista



def _import_scrapper_module(module_name: str):

    return importlib.import_module(f"torrent_scrapping_modules.{(module_name.removesuffix('.py'))}")





def search_torrent_with_module(movie_name : str, module_name : str) -> str:
    """
    Encuentra un listado de películas disponibles para descargar y sus respectivos links de descarga a partir del nombre de la película y el módulo de scrapping que se quiera utilizar.
    """

    module = _import_scrapper_module(module_name)
    return module.search_torrent(movie_name)
        
    

  
def get_torrent_from_link_with_module(link : str, module_name : str) -> str:
    """
    Ejecuta la descarga de un archivo .torrent a partir de un link obtenido en la función search_torrent y el módulo de scrapping que se quiera utilizar.
    """

    module = _import_scrapper_module(module_name)
    return module.get_torrent_from_link(link)

    

if __name__ == "__main__":
    print(get_available_modules())
    module = "don_torrent_module"
    rprint(search_torrent_with_module("spiderman", module))
    #link = 'https://www.publicdomaintorrents.info/nshowmovie.html?movieid=253'
    #rprint(get_torrent_from_link_with_module(link, module))
