from models import Author, Quote
import connect
import json
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

mongo_user = config.get('DB', 'user')
mongodb_pass = config.get('DB', 'pass')
db_name = config.get('DB', 'db_name')
domain = config.get('DB', 'domain')

client = MongoClient(
    f"""mongodb+srv://{mongo_user}:{mongodb_pass}@{domain}/{db_name}?retryWrites=true&w=majority""",
    server_api=ServerApi('1'))

def json_to_db(file_name, db):
    with open(file_name) as file:
        file_data = json.load(file)

    if isinstance(file_data, list):
        db.insert_many(file_data)  
    else:
        db.insert_one(file_data)


aut = Author(fullname = 'Dimitri', born_date = '1.1.2021', born_location = 'In the middle of nowhere', description = 'The dude.').save()
tag = Quote(tags = ['123','222','44'], author=aut, quote='There were 3 goats. How many? You have 30 seconds - Jacques Fresko').save()
tag = Quote(tags = ['123','222','44'], author=aut, quote='"I didnt say that" - Jacques Fresko').save()

def parse_data():
    url = 'https://quotes.toscrape.com/'
    quotes = []
    authors = []
    html_doc = requests.get(url)

    if html_doc.status_code == 200:
        soup = BeautifulSoup(html_doc.content, 'html.parser')
        books = soup.select('body')[0].find_all('div', attrs={'class': 'quote'})
        for book in books:
            author = book.find('small', attrs={'class': 'author'}).get_text()
            quote = book.find('span', attrs={'class': 'text'}).get_text()
            tags_raw = book.find('div', attrs={'class': 'tags'}).find_all('a', attrs={'class': 'tag'})#.get_text()
            tags = []
            for i in tags_raw:
                tags.append(i.get_text())

            author_link = "https://quotes.toscrape.com" + book.find('a').get('href')
            au_soup = BeautifulSoup(requests.get(author_link).content, 'html.parser')
            au_info = au_soup.select('body')[0].find('div', attrs={'class': 'author-details'})
            fullname = au_info.find('h3', attrs={'class': 'author-title'}).get_text()
            born_date = au_info.find('span', attrs={'class': 'author-born-date'}).get_text()
            born_location = au_info.find('span', attrs={'class': 'author-born-location'}).get_text()
            description = au_info.find('div', attrs={'class': 'author-description'}).get_text()
            
            quotes.append({
                'tags': tags,
                'author': author,
                'quote': quote
            })
            check = False
            for item in authors:
                if item['fullname'] == fullname:
                    check = True
            if not check:
                authors.append({
                    'fullname': fullname,
                    'born_date': born_date,
                    'born_location': born_location,
                    'description':description
                })

    with open('quotes.json', 'w') as file:
        file_data = json.dump(quotes, file, indent=2)
        
    with open('authors.json', 'w') as file:
        file_data = json.dump(authors, file, indent=2)

if __name__ == '__main__':
    parse_data()
    json_to_db('authors.json', client.myFirstDatabase.author)
    json_to_db('quotes.json', client.myFirstDatabase.quote)