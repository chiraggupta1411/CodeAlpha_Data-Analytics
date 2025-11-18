import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

def scrape_imdb_top250():
    """
    Scrape IMDb Top 250 movies list
    """
    url = "https://www.imdb.com/chart/top/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    print("🎬 Scraping IMDb Top 250 Movies...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        movies = []
        
        # Find all movie items in the list
        # IMDb uses <li> elements with class containing 'ipc-metadata-list'
        movie_items = soup.find_all('li', class_='ipc-metadata-list-summary-item')
        
        print(f"Found {len(movie_items)} movies")
        
        for idx, item in enumerate(movie_items, 1):
            try:
                # Extract movie title
                title_elem = item.find('h3', class_='ipc-title__text')
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    # Remove ranking number (e.g., "1. The Shawshank Redemption" -> "The Shawshank Redemption")
                    title = title_text.split('. ', 1)[1] if '. ' in title_text else title_text
                else:
                    title = 'N/A'
                
                # Extract year
                year_elem = item.find('span', class_='sc-b189961a-8')
                year = year_elem.get_text(strip=True) if year_elem else 'N/A'
                
                # Extract rating
                rating_elem = item.find('span', class_='ipc-rating-star')
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    rating = rating_text.split()[0] if rating_text else 'N/A'
                else:
                    rating = 'N/A'
                
                # Extract IMDb link
                link_elem = item.find('a', class_='ipc-title-link-wrapper')
                movie_link = f"https://www.imdb.com{link_elem['href']}" if link_elem and 'href' in link_elem.attrs else 'N/A'
                
                # Extract movie ID from URL
                movie_id = 'N/A'
                if movie_link != 'N/A':
                    try:
                        movie_id = movie_link.split('/title/')[1].split('/')[0]
                    except:
                        pass
                
                movies.append({
                    'rank': idx,
                    'title': title,
                    'year': year,
                    'rating': rating,
                    'imdb_id': movie_id,
                    'url': movie_link
                })
                
                # Progress indicator
                if idx % 50 == 0:
                    print(f"  Processed {idx} movies...")
                
            except Exception as e:
                print(f"  ⚠ Error parsing movie {idx}: {e}")
                continue
        
        return movies
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching IMDb: {e}")
        return []

def save_results(movies, format='all'):
    """
    Save scraped data in multiple formats
    """
    if not movies:
        print("No data to save!")
        return
    
    df = pd.DataFrame(movies)
    
    # CSV
    if format in ['all', 'csv']:
        csv_file = 'imdb_top250.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"✓ Saved to {csv_file}")
    
    # JSON
    if format in ['all', 'json']:
        json_file = 'imdb_top250.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved to {json_file}")
    
    # Excel
    if format in ['all', 'excel']:
        excel_file = 'imdb_top250.xlsx'
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"✓ Saved to {excel_file}")
    
    # Display summary
    print(f"\n📊 Summary:")
    print(f"   Total movies: {len(movies)}")
    print(f"   Top 5 movies:")
    for movie in movies[:5]:
        print(f"   {movie['rank']}. {movie['title']} ({movie['year']}) - ⭐ {movie['rating']}")

def get_movie_details(movie_url):
    """
    Optional: Get additional details for a specific movie
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(movie_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        details = {}
        
        # Extract director
        director_elem = soup.find('a', class_='ipc-metadata-list-item__list-content-item')
        details['director'] = director_elem.get_text(strip=True) if director_elem else 'N/A'
        
        # Extract plot summary
        plot_elem = soup.find('span', class_='sc-466bb6c-2')
        details['plot'] = plot_elem.get_text(strip=True) if plot_elem else 'N/A'
        
        # Extract runtime
        runtime_elem = soup.find('li', class_='ipc-inline-list__item', string=lambda x: x and 'h' in str(x))
        details['runtime'] = runtime_elem.get_text(strip=True) if runtime_elem else 'N/A'
        
        return details
        
    except Exception as e:
        print(f"Error getting movie details: {e}")
        return {}

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("IMDb TOP 250 MOVIES SCRAPER")
    print("=" * 60)
    
    # Scrape the top 250 list
    movies = scrape_imdb_top250()
    
    if movies:
        # Save in all formats
        save_results(movies, format='all')
        
        print("\n" + "=" * 60)
        print("✅ Scraping completed successfully!")
        print("=" * 60)
        
        # Optional: Get detailed info for top 5 movies
        # Uncomment the code below if you want detailed information
        # print("\n🔍 Getting detailed information for top 5 movies...")
        # for movie in movies[:5]:
        #     if movie['url'] != 'N/A':
        #         print(f"\nFetching details for: {movie['title']}")
        #         details = get_movie_details(movie['url'])
        #         movie.update(details)
        #         time.sleep(2)  # Be respectful with delays
        
    else:
        print("\n❌ Failed to scrape movies. Please check your internet connection.")
        print("Note: IMDb may have updated their HTML structure.")
        print("Try using Selenium for JavaScript-rendered content.")

# ============================================
# ALTERNATIVE: Using Selenium for Dynamic Content
# ============================================

def scrape_with_selenium():
    """
    Alternative method using Selenium for JavaScript-rendered content
    Uncomment and install: pip install selenium webdriver-manager
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get('https://www.imdb.com/chart/top/')
        
        # Wait for content to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ipc-metadata-list")))
        
        # Get page source and parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Continue with parsing logic...
        
    finally:
        driver.quit()