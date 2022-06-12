import util
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import collections
import networkx as nx
import matplotlib.pyplot as plt
import pydot
'''
returns the basic header info from a person's profile
'''
def get_player_info(name, session):
    name = name.lower()
    info = {}
    if name not in util.get_player_ids().keys():
        info['name'] = name
        info['inactive'] = True
        return info
    player_url = 'https://learnedleague.com' + util.get_player_ids()[name]
    soup = util.url_to_bs(player_url, session)
    header = [a.text.strip() for a in soup.findAll('div', {'class': 'demog'})]
    info['inactive'] = False
    info['name'] = soup.find('h1', {'class': 'namecss'}).text
    info['img-src'] = soup.find('img', {'class': 'flagimg profflag'})['src']
    for h in header:
        if len(h) <= 1:
            break
        info[h.split(': ')[0].lower()] = h.split(': ')[1]
    return info


'''
returns the different charts listed in the tabs of a person's profile
1 - categories
2 - season statlines
3 - minileagues
4 - onedays
5 - referrals
6 - awards
7 - past seasons
8 - head to head
'''
def get_player_charts(name, session, pages):
    table_names = {
            1: [{'class': ["std sortable this_sea std_bord"]}, ['categories']],
            2: [{'class': ["std std_bord stats"]}, ['career stats']],
            3: [{'class': ["std onedaytbl stats"]}, ['minileagues']],
            4: [{'class': ["std stats", "std onedaytbl stats"]}, ['od-smiths', 'midseasons', 'onedays']],
            5: [{'class': ["std std_bord noback"]}, ['first', 'second', 'third']],
            6: [{'class': ["std std_bord stats"]}, ['awards']],
            7: [{'class': ["std this_sea"]}, ['season']],
            8: [{'class': ["std sortable h2h std_bord"]}, ['h2h']],
            }
    player_data = {}
    for p in pages:
        player_url = 'https://learnedleague.com' + util.get_player_ids()[name.lower()] + "&" + str(p)
        soup = util.url_to_bs(player_url, session)
        table = soup.findAll("table", table_names[p][0])
        for i, t in enumerate(table):
            t = re.sub(r'<tr .*>', r'<tr>', str(t))
            df = pd.read_html(t, header=0)
            if p == 4 and 'Topic' in list(df):
                player_data['od-smiths'] = df
            elif p == 4 and 'Classic' in list(df):
                player_data['midseasons'] = df
            elif p == 4 and 'One-Day' in list(df):
                player_data['onedays'] = df
            elif p == 7:
                player_data['season{}'.format(93-i)] = df
            else:
                player_data[table_names[p][1][i]] = df

    return player_data

def get_player_referrals(name, session):
    return get_player_charts(name, session, [5])

def get_player_branch(name, session):
    branch_url = 'https://learnedleague.com/branch.php?' + util.get_player_ids()[name.lower()].split('?')[1]
    soup = util.url_to_bs(branch_url, session)

    table = soup.find("table", "md std")
    df = pd.read_html(table.prettify(), header=0)
    dag = collections.defaultdict(list)
    for player in df[0]['Player.1']:
        print(player)
        g = get_player_referrals(player, session)
        if len(g) == 0:
            continue
        dag[player] = list(g['first'][0]['Player'])
        dag[get_player_info(player, session)['referrer']].append(player)

    G = nx.DiGraph(dag)
    pos = nx.nx_pydot.graphviz_layout(G)
    nx.draw(G, pos=pos, with_labels=True)

    plt.show()



