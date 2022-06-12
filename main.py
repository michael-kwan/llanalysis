import sys
sys.path.insert(0, './src')

import util
import player
from bs4 import BeautifulSoup
import requests
if __name__ == "__main__":
   sesh = util.login()
   #players = util.get_player_ids()
   #print(player.get_player_info('kwanm', sesh))
   #print(player.get_player_charts('kwanm', sesh, [5]))
   print(player.get_player_branch('boreckim', sesh))
