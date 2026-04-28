import os
import sys
import importlib
from pathlib import Path
from rich import print as rprint




def get_available_modules() -> list[str]:
    """
    Devuelve una lista de los módulos de scrapping disponibles.
    """

    modules_dir = Path(__file__).resolve().parent / "torrent_scrapping_modules"
    lista = os.listdir(modules_dir)

    lista = [module for module in lista if module.endswith(".py") and module != "__init__.py"]

    return lista



def _resolve_scrapper_module_name(module_name: str) -> str:
    module_name = module_name.removesuffix(".py").strip()

    available_modules = [Path(module).stem for module in get_available_modules()]

    if module_name in available_modules:
        return module_name

    partial_matches = [
        module for module in available_modules
        if module.startswith(module_name) or module_name in module
    ]

    if len(partial_matches) == 1:
        return partial_matches[0]

    raise ModuleNotFoundError(
        f"No se encontró un módulo de scrapping llamado '{module_name}'. Disponibles: {', '.join(available_modules)}"
    )


def _import_scrapper_module(module_name: str):

    resolved_module_name = _resolve_scrapper_module_name(module_name)

    if __package__:
        return importlib.import_module(
            f".torrent_scrapping_modules.{resolved_module_name}",
            package=__package__,
        )

    tools_dir = Path(__file__).resolve().parent
    parent_dir = tools_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    return importlib.import_module(f"tools.torrent_scrapping_modules.{resolved_module_name}")





def search_torrent_with_module(movie_name : str, module_name : str) -> str:
    """
    Encuentra un listado de películas disponibles para descargar y sus respectivos links de descarga a partir del nombre de la película y el módulo de scrapping que se quiera utilizar.
    Debes pasar dos strings a esta función.
    """

    print(f"LOGS: Buscando torrents para {movie_name} con el módulo {module_name}")

    module = _import_scrapper_module(module_name)
    return module.search_torrent(movie_name)
        
    

  
def get_torrent_from_link_with_module(link : str, module_name : str) -> str:
    """
    Ejecuta la descarga de un archivo .torrent a partir de un link obtenido en la función search_torrent_with_module y el módulo de scrapping que se quiera utilizar.
    Debes pasar dos strings a esta función.
    """

    print(f"LOGS: Descargando torrent desde {link} con el módulo {module_name}")

    module = _import_scrapper_module(module_name)
    return module.get_torrent_from_link(link)

    

if __name__ == "__main__":
    print(get_available_modules())
    module = "public_domain_module.py"
    rprint(search_torrent_with_module("a boy", module))
    #link = 'https://www.publicdomaintorrents.info/nshowmovie.html?movieid=253'
    #rprint(get_torrent_from_link_with_module(link, module))