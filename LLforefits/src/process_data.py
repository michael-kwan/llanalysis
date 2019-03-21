from bs4 import BeautifulSoup as bs
import requests
import json

INPUTDATA = 'login.ini'
LOGINFILE = 'https://www.learnedleague.com/ucp.php?mode=login'

def login():
    logindetails = json.load(open('logindata.json'))
    payload = {'login': 'Login'}
    payload['username'] = logindetails['learnedleague']['username']
    payload['password'] = logindetails['learnedleague']['password']
    ses1 = requests.Session()
    ses1.post(LOGINFILE, data=payload)
    return ses1

def read_dataset(path_to_dataset, filename):
    players = []
    with open(path_to_dataset+"/"+filename) as f:
        for line in f.readlines():
            name = line.strip()
            name.replace(" ", "_")
            players.append(name)
    return players


def get_player_stats(player_name, session=login()):
    url = "https://learnedleague.com/profiles/previous.php?" + player_name.lower()
    r = session.get(url)
    data = r.content
    page = bs(data, features="html.parser")
    tables = page.findAll("table", {"class": "std"})
    seasons = len(tables)
    totalforefits = 0
    try:
        for table in tables:
            midLeft = table.findAll("td", {"class": "std-midleft"})
            counter = 0
            forefits = 0
            for e in midLeft:
                try:
                    if 'match' in e.find('a')['href'] or 'questions' in e.find('a')['href']:
                        statline = e.text
                        if '0(F)-' in statline:
                            forefits += 1
                        counter += 1
                except:
                    continue
            forefits = forefits/counter * 25
            totalforefits += forefits
        ffr = totalforefits/25/seasons
        if ffr < 0.16714285714285712:
            success = 0
        else:
            success = 1
        return ffr, success
    except:
        print ("error occured for " + player_name)
        return 0, 0

get_player_stats('barbt')