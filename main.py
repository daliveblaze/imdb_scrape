import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import email, smtplib, ssl

import subprocess
from email.message import EmailMessage

import glob
import codecs

def sendEmail(from_addr, to_addrs, msg_subject, msg_body):
    msg = EmailMessage()
    msg.set_content(msg_body)
    msg['From'] = from_addr
    msg['To'] = to_addrs
    msg['Subject'] = msg_subject

    sendmail_location = "/usr/sbin/sendmail"
    subprocess.run([sendmail_location, "-t", "-oi"], input=msg.as_bytes())


# initialize storage
titles = []
links = []
years = []
roles = []
filmo = []
imdb_url = "https://www.imdb.com/"

filepath = "mwf_acting.csv"

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

# Build dataframe to store data
movies = pd.DataFrame( {
    'movie': titles,
    'link' : links,
    'year' : years,
    'role' : roles,
})

# Clean it
movies['year'] = movies['year'].str.replace('\n', '')
movies['year'] = movies['year'].str.strip()

acting = movies.loc[movies['role'] == "Actor"]
acting = acting.reset_index(drop=True)
print(acting)
# Output the CSV
acting.to_csv(filepath, index=False, encoding='utf-8')

length = len(acting)    #length of acting list
acting_list = ""
i = 0
while i < length:
    acting_list = acting_list + "<li><a href=\"" + acting.loc[i][1] + "\">" + acting.loc[i][0] + " (" + acting.loc[i][2] + ")</a></li>"
    i = i+1
print("Here is the acting list to insert: " + acting_list)

filename = "/var/www/markwahlbergfan.com/public_html/index.htm"

with codecs.open(filename, 'r', encoding='cp1252') as f:
    print("Reading file contents of " + filename)
    contents = f.read()
    # Parse file contents with bs4 and store
    soup = BeautifulSoup(contents, "html.parser")
    new_content = str(soup) # newly parsed contents
    section = soup.find('div')
    acting_list = "<div>"+acting_list+"</div>"
    
    new_content = new_content.replace(str(section), acting_list)
    print(new_content)
    print("Closing the file " + filename)
    f.close()
with codecs.open(filename, 'w', encoding='cp1252') as w:
    print("Saving new file contents of " + filename)
    w.write(new_content)
    w.close()


msg_body = acting_list
#print(msg_body)

msg_subject = "MWF Subject"
from_addr = "dal@liveblaze.com"
to_addrs = "dalconhai@gmail.com"

sendEmail(from_addr, to_addrs, msg_subject, msg_body)