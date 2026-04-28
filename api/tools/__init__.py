from .film_scrapper import search_movie
from .cartelera_madrid import get_movie_info, get_cartelera_madrid, format_movie, format_cartelera_message
from .profiling import ProfileManager # Las tools son los metodos de la clase.
from .q_bit_torrent import get_available_torrent_files, download_torrent_file, get_torrent_client_status, remove_torrent_file
from .torrent_scrapper import get_available_modules, search_torrent_with_module, get_torrent_from_link_with_module