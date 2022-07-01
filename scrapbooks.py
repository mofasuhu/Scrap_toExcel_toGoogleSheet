import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

url = 'https://ar.wikipedia.org/wiki/قائمة_أفضل_مئة_رواية_عربية'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'lxml')
Table = soup.find('table', class_='wikitable sortable')
list_data = []
for tr in Table.find_all('tr')[1:]:
    tds = tr.find_all('td')
    order = tds[0].contents[0][:-1]
    book = tds[1].a.contents[0]
    book_link = f"https://ar.wikipedia.org/{tds[1].a.get('href')}"
    author = tds[2].a.contents[0]
    author_link = f"https://ar.wikipedia.org/{tds[2].a.get('href')}"
    country = tds[3].a.contents[0]
    country_link = f"https://ar.wikipedia.org/{tds[3].a.get('href')}"
    list_data.append({'الترتيب': int(order),
                      'الرواية': str(book),
                      'صفحة_الرواية': book_link,
                      'المؤلف': author,
                      'صفحة_المؤلف': author_link,
                      'البلد': country,
                      'صفحة_البلد': country_link})

df = pd.DataFrame(list_data)

with pd.ExcelWriter('books.xlsx') as writer:
    df.to_excel(writer, sheet_name='books', index=False, encoding='utf-16')
    writer.sheets['books'].right_to_left()

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Best_Arabic_Novels').sheet1

sheet.update([df.columns.values.tolist()] + df.values.tolist())
