# OnCourse Tutor Scraper

A Python-based web scraper for collecting tutor information from OpenAcademy Sydney's website.

## Features

- Extracts tutor URLs from the sitemap
- Scrapes tutor profiles including names and descriptions
- Saves data in CSV format
- Rate-limited to be server-friendly
- Command-line interface with testing limits
- UTF-8 encoding support

## Requirements

```bash
pip install requests beautifulsoup4
```

## Usage

To scrape detailed information for all tutors:

```bash
python scrape.py
```

With a limit (for testing):

```bash
python scrape.py --limit 5
```

This will create `data/tutors.csv` containing:

- Tutor URLs
- Tutor names
- Full profile descriptions

## Output

The scraped data is saved in the `data/` directory:

- `tutor_index.csv`: Basic index of tutor names and URLs
- `tutors.csv`: Detailed tutor information including full profiles

## Note

This scraper includes a 1-second delay between requests to avoid overwhelming the server. Please use responsibly and in accordance with the website's terms of service.
