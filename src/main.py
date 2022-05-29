import util
from bs4 import BeautifulSoup
import requests
if __name__ == "__main__":
   sesh = util.login()
   players = util.get_player_ids(sesh)


