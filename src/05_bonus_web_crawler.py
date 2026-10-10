# BONUS WEBSITE: https://books.toscrape.com/catalogue/page-1.html
"""Optional extra credit: real web crawling, target >=300 actual book records with >=8 static fields.
Runs only with internet access; respects robots.txt and polite throttling.
Outputs data/raw/bonus_books_scraped.csv; DOES NOT fabricate scraped rows.
This bonus is a standalone acquisition demonstration, not a feed for the Gapminder model.
"""
from pathlib import Path
from urllib.parse import urljoin,urlparse
from urllib.robotparser import RobotFileParser
import time
import requests,pandas as pd
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
BASE='https://books.toscrape.com/'
UA='University-DataAnalystAI-Project/1.0 (educational; polite 1s delay)'

def get(session,url):
    r=session.get(url,timeout=18);r.raise_for_status();time.sleep(1.0)
    return BeautifulSoup(r.text,'html.parser')

def main():
    s=requests.Session();s.headers.update({'User-Agent':UA})
    rules=RobotFileParser();rules.set_url(urljoin(BASE,'robots.txt'))
    try: rules.read()
    except Exception as e: raise RuntimeError('Unable to verify robots policy; abort crawling') from e
    rows=[]
    for p in range(1,36): # 35 * 20 = up to 700 real rows
        url=urljoin(BASE,f'catalogue/page-{p}.html')
        if not rules.can_fetch(UA,url): raise PermissionError('robots.txt disallows '+url)
        try: doc=get(s,url)
        except requests.RequestException as e:
            print('Stopped on inaccessible page:',url,e);break
        cards=doc.select('article.product_pod')
        if not cards:break
        for card in cards:
            a=card.select_one('h3 a')
            if not a:continue
            detail_url=urljoin(url,a.get('href',''))
            rating=next((v for v in card.select_one('.star-rating').get('class',[]) if v!='star-rating'),'Unknown')
            avail=card.select_one('.availability').get_text(' ',strip=True)
            image=card.select_one('img')
            rows.append({'book_id':urlparse(detail_url).path.rsplit('/',2)[-2],
               'title':a.get('title') or a.get_text(' ',strip=True),
               'price_gbp':float(card.select_one('.price_color').get_text(strip=True).replace('£','')),
               'star_rating_text':rating,'in_stock':bool('In stock' in avail),
               'availability_text':avail,'product_url':detail_url,
               'image_url':urljoin(url,image.get('src','')) if image else '',
               'page_number':p,'source_website':'books.toscrape.com'})
    df=pd.DataFrame(rows)
    if len(df)<300: raise RuntimeError(f'Only {len(df)} real records. Must rerun crawl to reach >=300; no fake filler.')
    if df.product_url.duplicated().any():raise ValueError('Duplicate book URLs')
    path=ROOT/'data/raw/bonus_books_scraped.csv';df.to_csv(path,index=False)
    print(f'Bonus crawl verified: {len(df)} products, {len(df.columns)} attributes, {path}')
if __name__=='__main__':main()
