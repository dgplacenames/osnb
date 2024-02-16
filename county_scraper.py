import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import os

# Replace 'folder_path' with the filepath of the folder you're saving to
folder_path = r'folder_path'

# Add Name Book county link here
county_url = "https://scotlandsplaces.gov.uk/digital-volumes/ordnance-survey-name-books/ayrshire-os-name-books-1855-1857"

end_date = county_url[-4:]
county_soup = BeautifulSoup(requests.get(county_url).content, 'html.parser')
volume_links = []

# Collects volume links
for i in county_soup.findAll('td', attrs={'style':'white-space: nowrap'}):
    a_link = i.find('a') 
    volume_link = a_link.get('href') 
    volume_links.append(volume_link)
    
# Converts volume links to full urls
for i in volume_links:
    volume_url= (f"https://scotlandsplaces.gov.uk{i}")
    # Creates filename in format 'county-volume-no'
    filename = i.split(end_date,1)[1]
    # Collects page links 
    volume_soup = BeautifulSoup(requests.get(volume_url).content, 'html.parser')
    page_links = [] 
    for i in volume_soup.findAll('td'):
        a_page = i.find('a')     
        page_link = a_page.get('href') 
        page_links.append(page_link)
    # Finds number of pages in volume
    pages = int(len(page_links)/2)+1

    res =[]
    # Collects data from pages
    for i in range(1,pages):
        page = f"{volume_url}/{i}"
        page_soup = BeautifulSoup(requests.get(page).content, 'html.parser')
        map_urls = []
        # Collects page id
        title = page_soup.find('title').text
        os_id = re.search('(.+) \|',title).group(1)
        # Collects text from 'Continued entries/extra info'
        panel_body = page_soup.find('div',{'class':'panel-body'}).get_text(' ', strip = True)
        try:
            extras = re.search('extra info((.|\n)*)',panel_body).group(1)
        except:
            pass
        # Collects linked mapsheet urls
        for i in page_soup.findAll('td'):
            a_mapsheet = i.find('a')
            try:
                'href' in a_mapsheet.attrs 
                map_url = f"https://scotlandsplaces.gov.uk{a_.get('href')}" 
                map_url.append(map_urls)
            except:
                pass
            
        # Collects data from table of entries and adds additional colums to dataframe 
        try:
            dfs = pd.read_html(page)
            df = dfs[0]
            df['url'] = page
            df['id'] = os_id
            df['extras'] = extras
            # Adds linked mapsheet urls to dataframe
            try:
                for index, item in enumerate(map_links):
                    n = index +1
                    df[f"map_sheet{n}"] = item
            except:
                pass
            res.append(df)
            
        # Collects data from pages without table of entries
        except:
            data = {
                    "List of names as written": [""],
                    "Various modes of spelling": [""],
                    "Authorities for spelling": [""],
                    "Situation": [""],
                    "Description remarks": [""],
                    "url": [page],
                    "id": [os_id],
                    "extras": [extras],
                    }
            df = pd.DataFrame(data)
            res.append(df)
        
        # Saves volume
        pd.concat(res).to_csv(fr'{folder_path}{filename}.csv')
        
        # Prints pages added to volumes
        print(page.split(end_date,1)[1])

# Combines all volumes into additional file
all_files = os.listdir(folder_path)

# Filters out non-CSV files
csv_files = [f for f in all_files if f.endswith('.csv')]

# Creates a list to hold the dataframes
df_list = []

for csv in csv_files:
    file_path = os.path.join(folder_path, csv)
    df = pd.read_csv(file_path)
    df_list.append(df)

# Concatenates all data into one DataFrame
combined_df = pd.concat(df_list, ignore_index=True)

# Saves the final result to a new CSV file
combined_df.to_csv(os.path.join(folder_path, 'all_volumes.csv'), index=False)

print('Finished')
