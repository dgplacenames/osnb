import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

#add Name Book county link here
url = "https://scotlandsplaces.gov.uk/digital-volumes/ordnance-survey-name-books/ayrshire-os-name-books-1855-1857"
end_date = url[-4:]
soup = BeautifulSoup(requests.get(url).content, 'html.parser')
urls = []

for h in soup.findAll('td', attrs={'style':'white-space: nowrap'}):
    a = h.find('a') 
    url_ = a.get('href') 
    urls.append(url_)

for i in urls:
    url= (f"https://scotlandsplaces.gov.uk{i}")
    
    filename = i.split(end_date,1)[1]
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    urls = [] 
    for h in soup.findAll('td'):
        a = h.find('a') 
        #if 'href' in a.attrs: 
        url_ = a.get('href') 
        urls.append(url_)
    no = int(len(urls)/2)+1
    res =[]

    for count in range(1,no):
        page = f"{url}/{count}"
        html = urlopen(page).read().decode("utf-8")  
        id_start = html.find('<title>') +7
        id_end = html.find(' |', id_start)
        end_index = html.find("</title>")
        os_id = html[id_start:id_end]
        extras_start = html.find('</h2>') +5
        extras_end = html.find('</div>', extras_start)
        extras = html[extras_start:extras_end].strip()  
        try:
            dfs = pd.read_html(page)
            df = dfs[0]
            df['url'] = page
            df['id'] = os_id
            df['extras'] = extras
            res.append(df)
        except:
            data = {
                    "List of names as written": [""],
                    "Various modes of spelling": [""],
                    "Authorities for spelling": [""],
                    "Situation": [""],
                    "Description remarks": [""],
                    "url": [page],
                    "id": [os_id],
                    "extras": [extras]
                    }
            df = pd.DataFrame(data)
            res.append(df)
        
        #add your filepath between r'.csv
        pd.concat(res).to_csv(fr'path{filename}.csv')
        print(page.split(end_date,1)[1])
    
