from bs4 import BeautifulSoup as bs
import requests
import json
import numpy as np
import csv

def login():
    logindetails = json.load(open('./logindata.json'))
    payload = {'login': 'Login'}
    payload['username'] = logindetails['learnedleague']['username']
    payload['password'] = logindetails['learnedleague']['password']
    ses1 = requests.Session()
    ses1.post('https://www.learnedleague.com/ucp.php?mode=login', data=payload)
    print("created new session with login {}".format(payload['username']))
    return ses1

def get_player_ids(session=None):
    players2 = {}
    if not session:
        print("retrieving players from local")
        reader = csv.reader(open('./data/players.csv', 'r'))
        for row in reader:
            k, v = row
            players2[k] = v
    else:
        print("retrieving players from remote")
        url = 'https://learnedleague.com/backend-search.php?term='
        r = session.get(url)
        data = r.content
        soup = bs(data, features='html.parser')
        players = []
        for link in soup.find_all('a', href=True):
            row = [link.p.span.text.lower(), link['href']]
            players.append(row)
            players2[link.p.span.text.lower()] = link['href']
        np.savetxt("./data/players.csv", players, delimiter=',', fmt='% s')
    return players2

