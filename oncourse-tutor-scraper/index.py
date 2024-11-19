import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import csv
import argparse
import time

def get_tutor_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    root = ET.fromstring(response.content)
    
    tutor_urls = []
    for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        if '/tutor/' in loc:
            tutor_urls.append(loc)
    
    return tutor_urls

def get_tutor_name(url):
    time.sleep(1)  # Be nice to the server
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    try:
        article = soup.find('article', id='content')
        if article and article.find('h2'):
            return article.find('h2').text.strip()
        else:
            return f"Tutor {url.split('/')[-1]}"
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return f"Tutor {url.split('/')[-1]}"

def create_index(urls, limit=None):
    def create_index(urls, limit=None):
    if limit:
        urls = urls[:limit]
    
    index_data = []
    for i, url in enumerate(urls, 1):
        print(f"Processing {i} of {len(urls)}: {url}")
        name = get_tutor_name(url)
        index_data.append([name, url])
    
    return index_data

def save_to_csv(data, filename='tutor_index.csv'):
    # Create data directory if it doesn't exist
    import os
    os.makedirs('data', exist_ok=True)
    
    # Save file in the data directory
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'URL'])
        writer.writerows(data)

def main():
    parser = argparse.ArgumentParser(description='Create tutor URL index')
    parser.add_argument('--limit', type=int, help='Limit the number of tutors to process')
    args = parser.parse_args()

    sitemap_url = 'https://openacademy.sydney.edu.au/sitemap.xml'
    
    print("Getting tutor URLs from sitemap...")
    urls = get_tutor_urls_from_sitemap(sitemap_url)
    
    if args.limit:
        print(f"Limited to first {args.limit} URLs for testing")
    
    print("Creating index...")
    index_data = create_index(urls, args.limit)
    
    save_to_csv(index_data)
    print(f"Index saved to data/tutor_index.csv")

if __name__ == "__main__":
    main()