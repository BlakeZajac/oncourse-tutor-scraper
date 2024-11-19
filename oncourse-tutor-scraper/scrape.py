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
    # Add 5 seconds delay to be considerate to the server
    time.sleep(5)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            break  # If successful, break out of retry loop
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:  # Last attempt
                print(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                return (url, f"tutor_{url.split('/')[-1]}", "Failed to fetch content", "", "", "", "", "")
            print(f"Attempt {attempt + 1} failed, retrying after 10 seconds...")
            time.sleep(10)  # Wait longer between retries
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    try:
        # Try to get the tutor name first
        h2 = soup.find('h2')
        title = h2.text.strip() if h2 else f"tutor_{url.split('/')[-1]}"
        
        # Find the resume details div
        resume_div = soup.find('div', {'class': 'resume-details', 'itemprop': 'description'})
        if not resume_div:
            # Return empty data but with the title if we found it
            return (url, title, "", "", "", "", "", "")
        
        # Remove unwanted elements
        # Remove Resume heading
        resume_heading = resume_div.find('h4', string='Resume')
        if resume_heading:
            resume_heading.decompose()
            
        # Remove return to links paragraph
        return_p = resume_div.find('p', string=lambda t: t and 'Return to:' in t)
        if return_p:
            return_p.decompose()
            
        # Remove reserved classes message
        reserved_p = resume_div.find('p', string=lambda t: t and 'Any classes listed below' in t)
        if reserved_p:
            reserved_p.decompose()
        
        # Extract specific fields
        fields = {
            'Teaching': '',
            'Levels': '',
            'Ages': '',
            'Genres': '',
            'Available': ''
        }
        
        # Find all paragraphs with strong tags
        for p in resume_div.find_all('p'):
            for strong in p.find_all('strong'):
                field = strong.text.strip(':')
                if field in fields:
                    # Get the text after the strong tag
                    value = strong.next_sibling
                    if value:
                        fields[field] = value.strip()
                    strong.decompose()  # Remove the field label from content
        
        # Get remaining content
        content = resume_div.get_text(separator='\n', strip=True)
        
        # Create CSV row with additional columns
        return (
            url, 
            title, 
            content,
            fields['Teaching'],
            fields['Levels'],
            fields['Ages'],
            fields['Genres'],
            fields['Available']
        )
    except Exception as e:
        print(f"Error processing {url}: {e}")
        tutor_number = url.split('/')[-1]
        return url, f"tutor_{tutor_number}", "Failed to extract content", "", "", "", "", ""

def save_to_csv(tutors_data, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    csv_path = os.path.join(output_dir, 'tutors.csv')
    
    # Write to CSV with UTF-8 encoding
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write headers with new columns
        writer.writerow(['URL', 'Title', 'Description', 'Teaching', 'Levels', 'Ages', 'Genres', 'Available'])
        # Write tutor data
        writer.writerows(tutors_data)
    
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
    for idx, url in enumerate(tutor_urls, 1):
        print(f"Processing {idx} of {len(tutor_urls)}: {url}")
        tutor_data = scrape_tutor_page(url)  # Capture all returned values
        tutors_data.append(tutor_data)
        print(f"Processed content for {url}")
    
    # Save all data to CSV
    csv_path = save_to_csv(tutors_data, output_dir)
    print(f"Saved all tutor data to {csv_path}")

if __name__ == "__main__":
    main()