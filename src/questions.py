from bs4 import BeautifulSoup
import csv
import requests
import time
from urllib.parse import urljoin

class LearnedLeagueScraper:
   def __init__(self, base_url="https://learnedleague.com"):
       self.base_url = base_url
       self.session = requests.Session()

   def login(self, username, password):
       """Keeping login for future use but not requiring it"""
       login_url = urljoin(self.base_url, "/login.php")
       payload = {
           'username': username,
           'password': password
       }
       response = self.session.post(login_url, data=payload)
       return response.ok

   def get_match_content(self, season, match_day):
       url = f"{self.base_url}/match.php?{season}&{match_day}"
       response = self.session.get(url)
       if response.ok:
           return response.text
       else:
           raise Exception(f"Failed to fetch content from {url}: {response.status_code}")

   def parse_stats_table(self, soup):
       stats = {}
       rows = soup.find_all('tr')

       # Process each rundle level (A through R)
       levels = ['A', 'B', 'C', 'D', 'E', 'R']
       for level in levels:
           try:
               level_row = next(row for row in rows if f'All {level}' in row.find('td').text)
               percentages = [td.text.strip() for td in level_row.find_all('td')[2:8]]  # Skip Rundle and Forf%
               stats[f'{level.lower()}_pct'] = percentages
               # Add defense values for each rundle
               level_def_row = next((row for row in rows if row.find('td').text.strip() == f'{level} Defense'), None)
               if level_def_row:
                   defenses = [td.text.strip() for td in level_def_row.find_all('td')[2:8]]
                   stats[f'{level.lower()}_def'] = defenses
           except StopIteration:
               print(f"Warning: Could not find row for level {level}")
               stats[f'{level.lower()}_pct'] = ['0'] * 6
               stats[f'{level.lower()}_def'] = ['0'] * 6

       # Get leaguewide percentages
       try:
           leaguewide_row = next(row for row in rows if 'Leaguewide' in row.find('td').text)
           stats['all_pct'] = [td.text.strip() for td in leaguewide_row.find_all('td')[2:8]]
       except StopIteration:
           print("Warning: Could not find leaguewide stats")
           stats['all_pct'] = ['0'] * 6

       # Get overall defense values
       try:
           defense_row = next(row for row in rows if row.find('td').text.strip() == 'Defense')
           stats['all_def'] = [td.text.strip() for td in defense_row.find_all('td')[2:8]]
       except StopIteration:
           print("Warning: Could not find defense stats")
           stats['all_def'] = ['0'] * 6

       return stats

   def parse_questions(self, soup, season, match_day, stats):
       questions = []
       q_divs = soup.find_all('div', class_='ind-Q20')

       for idx, q_div in enumerate(q_divs, 1):
           try:
               # Get full text and split on first dash
               full_text = q_div.get_text(strip=True)
               try:
                   before_dash, question = full_text.split('-', 1)
                   # Remove the Q#. prefix to get category
                   category = before_dash[before_dash.find('.')+1:].strip()
               except ValueError:
                   print(f"Warning: Could not split category in question {idx}")
                   category = "UNKNOWN"
                   question = full_text

               # Find corresponding answer div
               answer_div = q_div.find_next('div', class_='answer3')
               answer = answer_div.find('div', class_='a-red').get_text(strip=True)

               q_dict = {
                   'season': season,
                   'match_day': match_day,
                   'question_number': idx,
                   'category': category,
                   'question': question.strip(),
                   'answer': answer,
                   'a_pct': stats['a_pct'][idx-1],
                   'b_pct': stats['b_pct'][idx-1],
                   'c_pct': stats['c_pct'][idx-1],
                   'd_pct': stats['d_pct'][idx-1],
                   'e_pct': stats['e_pct'][idx-1],
                   'r_pct': stats['r_pct'][idx-1],
                   'all_pct': stats['all_pct'][idx-1],
                   'a_def': stats.get('a_def', ['0']*6)[idx-1],
                   'b_def': stats.get('b_def', ['0']*6)[idx-1],
                   'c_def': stats.get('c_def', ['0']*6)[idx-1],
                   'd_def': stats.get('d_def', ['0']*6)[idx-1],
                   'e_def': stats.get('e_def', ['0']*6)[idx-1],
                   'r_def': stats.get('r_def', ['0']*6)[idx-1],
                   'all_def': stats['all_def'][idx-1]
               }
               questions.append(q_dict)
           except Exception as e:
               print(f"Error parsing question {idx}: {str(e)}")
               print(f"Full text was: {full_text}")

       return questions

   def scrape_match(self, season, match_day):
       html_content = self.get_match_content(season, match_day)
       soup = BeautifulSoup(html_content, 'html.parser')
       stats = self.parse_stats_table(soup)
       return self.parse_questions(soup, season, match_day, stats)

   def scrape_multiple_matches(self, seasons, match_days):
       all_questions = []

       for season in seasons:
           for match_day in match_days:
               try:
                   print(f"Scraping season {season}, match day {match_day}")
                   questions = self.scrape_match(season, match_day)
                   all_questions.extend(questions)
                   time.sleep(1)  # Be nice to the server
               except Exception as e:
                   print(f"Error scraping S{season}MD{match_day}: {str(e)}")

       return all_questions

def write_to_csv(questions, output_file):
   fieldnames = [
       'season', 'match_day', 'question_number', 'category', 'question', 'answer',
       'a_pct', 'b_pct', 'c_pct', 'd_pct', 'e_pct', 'r_pct', 'all_pct',
       'a_def', 'b_def', 'c_def', 'd_def', 'e_def', 'r_def', 'all_def'
   ]

   with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
       writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
       writer.writeheader()
       for q in questions:
           writer.writerow(q)

def main():
   scraper = LearnedLeagueScraper()

   # Define what to scrape
   seasons = range(60, 103)  # or multiple seasons: [102, 103]
   match_days = range(1, 26)

   # Just scrape directly without login
   questions = scraper.scrape_multiple_matches(seasons, match_days)
   output_file = 'learned_league_questions.csv'
   write_to_csv(questions, output_file)
   print(f"Data written to {output_file}")

if __name__ == "__main__":
   main()
