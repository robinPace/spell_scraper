import requests

from bs4 import BeautifulSoup
import pandas as pd
import time

# URL of the website to scrape
url = "http://dnd5e.wikidot.com/spells"

# Send an HTTP GET request to the website
response = requests.get(url)

# Parse the HTML code using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Extract the relevant information from the HTML code
links = []
page = soup.select(".list-pages-box")

for box in page:
    spellLinks = box.findAll('a', href=True)
    for link in spellLinks:
        spellUrl = "http://dnd5e.wikidot.com" + link['href']
        links.append(spellUrl)

df = pd.DataFrame(links, columns=['Link'])

df.to_csv('links.csv', index=False)