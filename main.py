import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


subject = "An email with attachment from Python"
body = "This is an email with attachment sent from Python"
sender_email = "liveblaze@gmail.com"
receiver_email = "dalconhai@gmail.com"
password = "Q7ct29EEh@$YJD"


# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message["Bcc"] = receiver_email  # Recommended for mass emails

# Add body to email
message.attach(MIMEText(body, "plain"))


# initialize storage
titles = []
links = []
years = []
roles = []
filmo = []
imdb_url = "https://www.imdb.com/"

filepath = "mwf_acting.csv"

# Open PDF file in binary mode
with open(filepath, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email    
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {filepath}",
)



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

# Output the CSV
acting.to_csv(filepath, index=False, encoding='utf-8')


# Open PDF file in binary mode
with open(filepath, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email    
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {filepath}",
)

# Add attachment to message and convert message to string
message.attach(part)
text = message.as_string()

# Log in to server using secure context and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, text)
