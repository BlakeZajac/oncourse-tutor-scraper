import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import os
import time
import csv
import argparse  # command line args

def get_tutor_urls_from_sitemap(sitemap_url):
    # Get sitemap content
    response = requests.get(sitemap_url)
    root = ET.fromstring(response.content)
    
    # Extract all tutor URLs
    tutor_urls = []
    for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        if '/tutor/' in loc:
            tutor_urls.append(loc)
    
    return tutor_urls

def scrape_tutor_page(url):
    # Add delay to be nice to the server
    time.sleep(1)
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    try:
        # Find the specific article tag
        article = soup.find('article', id='content')
        if not article:
            tutor_number = url.split('/')[-1]
            return url, f"tutor_{tutor_number}", "Failed to find content article"
        
        # Get the h2 for tutor name
        h2 = article.find('h2')
        if h2:
            title = h2.text.strip()
        else:
            tutor_number = url.split('/')[-1]
            title = f"tutor_{tutor_number}"
            
        # Get all text content from the article
        content = article.get_text(separator='\n', strip=True)
        
        return url, title, content
    except Exception as e:
        print(f"Error processing {url}: {e}")
        tutor_number = url.split('/')[-1]
        return url, f"tutor_{tutor_number}", "Failed to extract content"

def save_to_csv(tutors_data, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    csv_path = os.path.join(output_dir, 'tutors.csv')
    
    # Write to CSV with UTF-8 encoding
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write headers
        writer.writerow(['URL', 'Title', 'Description'])
        # Write tutor data
        for url, title, content in tutors_data:
            writer.writerow([url, title, content])
    
    return csv_path

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape tutor data')
    parser.add_argument('--limit', type=int, help='Limit the number of tutors to scrape (for testing)')
    args = parser.parse_args()

    sitemap_url = 'https://openacademy.sydney.edu.au/sitemap.xml'
    output_dir = 'data'
    
    # Get tutor URLs from sitemap
    print("Getting tutor URLs from sitemap...")
    tutor_urls = get_tutor_urls_from_sitemap(sitemap_url)
    
    # Apply limit if specified
    if args.limit:
        tutor_urls = tutor_urls[:args.limit]
        print(f"Limited to first {args.limit} URLs for testing")
    
    # Process each tutor URL and collect data
    print(f"Processing {len(tutor_urls)} tutor URLs")
    tutors_data = []
    for url in tutor_urls:
        print(f"Processing {url}")
        url, title, content = scrape_tutor_page(url)
        tutors_data.append((url, title, content))
        print(f"Processed content for {title}")
    
    # Save all data to CSV
    csv_path = save_to_csv(tutors_data, output_dir)
    print(f"Saved all tutor data to {csv_path}")

if __name__ == "__main__":
    main()