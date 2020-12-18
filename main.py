import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# initialize storage
titles = []
links = []
years = []
roles = []
filmo = []
imdb_url = "https://www.imdb.com/"

# make sure we get English-translated titles from all the movies we scrape:
headers = {"Accept-Language" : "en-US, en;q=0.5"}

# Request contents of the URL 
# Mark Wahlberg = nm0000242
url = "https://www.imdb.com/name/nm0000242/?ref_=fn_al_nm_1#actor"
results = requests.get(url, headers=headers)

# make content we grabbed easy to ready by using BS:
soup = BeautifulSoup(results.text, "html.parser")

# The header tells us whether it is Producer, Actor, etc, so get the headers
filmo_header_section = soup.find_all('div', class_='head')
for container in filmo_header_section:
    filmo.append(container.a.text)

# Now get sections, and for each section iterate the rows
filmo_category_section = soup.find_all('div', class_='filmo-category-section')
i = 0
for section in filmo_category_section:
    movie_div = section.find_all('div', class_="filmo-row")
    for container in movie_div:
        roles.append(filmo[i])  # set it according to header before
        name = container.b.a.text
        titles.append(name)
        link = imdb_url + container.b.a.get('href')
        links.append(link)
        year = container.find('span', class_='year_column').text
        years.append(year)
    i = i +1
print(i)

# Build dataframe to store data
movies = pd.DataFrame( {
    'movie': titles,
    'link' : links,
    'year' : years,
    'role' : roles,
})

# Clean it
movies['year'] = movies['year'].str.replace('\n', '')
movies['year'] = movies['year'].str.replace(' ', '')

acting = movies.loc[movies['role'] == "Actor"]

# Output the CSV
acting.to_csv("mwf_acting.csv", index=False, encoding='utf-8')
