from .film_scrapper import search_movie
from .cartelera_madrid import get_movie_info, scrape_cartelera_madrid, format_movie, format_cartelera_message
from .torrent_scrapping_modules.don_torrent_module import search_torrent, get_torrent_from_link
from .q_bit_torrent import get_available_torrent_files, download_torrent_file, get_torrent_client_status, remove_torrent_file
from .profiling import ProfileManager # Las tools son los metodos de la clase.
from torrent_srapper import get_available_modules, search_torrent_with_module, get_torrent_from_link_with_module, get_torrent_client_statusget_movie_info