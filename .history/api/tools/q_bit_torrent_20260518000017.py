import qbittorrentapi
from langchain.tools import tool
from rich import print as rprint
import os
from time import sleep

torrent_files_dir = "../torrents/"

print(os.getcwd())

conn_info = dict(
    host="localhost",
    port=8082,
    username="admin",
    password="316440",
)

def get_available_torrent_files() -> str:
    """Consigue la lista de archivos de torrent disponibles en nuestro sistema."""
    return os.listdir(torrent_files_dir)

def download_torrent_file(file_name: str) -> str:
    """Download a torrent file by its name."""
    with qbittorrentapi.Client(**conn_info) as qbt_client:
        qbt_client.torrents_add(
            torrent_files=[torrent_files_dir + file_name],
            savepath="/download",
            category="movies",
        )
    return f"Torrent file downloaded: {file_name}"


def get_torrent_client_status() -> str:
    """Ver la información de los torrents que se están descargando, el resultado es una lista de diccionarios con la siguiente información:
    - name: el nombre del torrent
    - dlspeed: la velocidad de descarga en MB/s
    - eta: el tiempo estimado de descarga en minutos
    - progress: el progreso de la descarga en porcentaje
    - size: el tamaño del torrent en GB
    - state: el estado del torrent (downloading, paused, etc.)
    - hash: el hash del torrent, un identificador único que se puede usar para eliminar el torrent de qbittorrent con la función `remove_torrent_file`
    - La función no recibe ningún argumento y devuelve una lista de diccionarios con la información de los torrents que se están descargando."""
    with qbittorrentapi.Client(**conn_info) as qbt_client:
        info = qbt_client.torrents_info()
        processed_info = []


        for info_dict in info:
            processed_info.append(dict())
            processed_info[-1]["name"] = info_dict["name"]        
            processed_info[-1]["dlspeed"] = info_dict["dlspeed"] / 1024 ** 2 
            processed_info[-1]["eta"] = info_dict["eta"] / 60
            processed_info[-1]["progress"] = info_dict["progress"] * 100
            processed_info[-1]["size"] = info_dict["size"] / (2 ** 30)
            processed_info[-1]["state"] = info_dict["state"]
            processed_info[-1]["hash"] = info_dict["hash"]
        
        print(info)


    return processed_info

def remove_torrent_file(hash: str) -> str:
    """
    Borra un archivo de torrent de qbittorrent por su hash.
    Solo borra el torrent de qbittorrent, no borra el archivo de torrent del sistema.
    El `hash` es un identificador único para cada torrent. Se puede obtener de la función `get_torrent_client_status`,
    que devuelve una lista de torrents con su información, incluyendo el hash.
    """
    with qbittorrentapi.Client(**conn_info) as qbt_client:
        qbt_client.torrents_delete(delete_files=False, torrent_hashes=hash)
    return f"Torrent file removed: {hash}"

if __name__ == "__main__":
    print(get_available_torrent_files())
    print(download_torrent_file("La_lista_de_Schindler_1993_HDRip.torrent"))
    rprint(get_torrent_client_status())

