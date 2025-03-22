from collections import Counter
import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from googletrans import Translator
import re

load_dotenv()
# RapidAPI Translate API setup
TRANSLATE_URL = "https://google-translate113.p.rapidapi.com/api/v1/translator/text"
TRANSLATE_HEADERS = {
    "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
    "Content-Type": "application/json"
}

def scrape_articles(driver):
    # Load main page and handle cookie popup
    driver.get("https://elpais.com/")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
    )
    time.sleep(1)  # Brief pause for stability
    driver.find_element(By.ID, "didomi-notice-agree-button").click()        

    # Navigate to opinion section
    driver.find_element(By.LINK_TEXT, "Opinión").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "c_t"))
    )
    
    # Get first 10 articles
    articles = driver.find_elements(By.CLASS_NAME, "c")[:10] 
    article_data = []
    
    # Extract data from each article
    for article in articles:
        try:
            title = article.find_element(By.CLASS_NAME, "c_t").text.strip()
            if not title:
                continue
            
            # Get article description if available
            try:
                content = article.find_element(By.CLASS_NAME, "c_d").text.strip()
            except:
                content = "No article description"
            
            # Try to get article image
            image_url = None
            try:
                image_url = article.find_element(By.TAG_NAME, "img").get_attribute("src")
            except:
                pass
            
            article_data.append({"title": title, "content": content, "image_url": image_url})
            if len(article_data) == 5:  # Only need first 5 articles
                break
        except Exception as e:
            print(f"Skipping an article due to error: {e}")
            continue
    
    return article_data

def download_image(image_url, title):
    # Save article images locally
    if image_url and title:
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                filename = title.replace(' ', '_')[:50] + ".jpg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded image for '{title}' as {filename}")
        except Exception as e:
            print(f"Failed to download image: {e}")

def translate_titles(article_data):
    # Translate article titles to English
    for article in article_data:
        payload = {
            "from": "es",
            "to": "en",
            "text": article["title"]
        }
        try:
            response = requests.post(TRANSLATE_URL, json=payload, headers=TRANSLATE_HEADERS)
            response.raise_for_status()
            translated_text = response.json().get("trans", "Translation failed")
            article["translated_title"] = translated_text
        except requests.exceptions.RequestException as e:
            print(f"Translation failed for '{article['title']}': {e}")
            article["translated_title"] = "Translation failed"
    return article_data

def analyze_repeated_words(article_data):
    all_words = []
    for article in article_data:
        if article["translated_title"] != "Translation failed":
            words = [word.lower() for word in article["translated_title"].split()]
            all_words.extend(words)
    word_counts = Counter(all_words)
    repeated_words = {word: count for word, count in word_counts.items() if count > 2}
    if repeated_words:
        print("\nWords repeated more than twice in translated headers:")
        for word, count in repeated_words.items():
            print(f"'{word}': {count} times")
    else:
        print("\nNo words repeated more than twice in translated headers.")

def main():

    driver = webdriver.Chrome()
    
    try:
        # Scrape articles
        article_data = scrape_articles(driver)
        if not article_data:
            print("No articles scraped successfully. Check selectors or network.")
            return
        
        # Print article details
        print("\nScraped Articles:")
        for i, article in enumerate(article_data, 1):
            print(f"\nArticle {i}:")
            print(f"Title (Spanish): {article['title']}")
            print(f"Content: {article['content']}")
            if article["image_url"]:
                print(f"Image URL: {article['image_url']}")
            download_image(article["image_url"], article["title"])
        
        # Translate titles
        article_data = translate_titles(article_data)
        print("\nTranslated Titles:")
        for i, article in enumerate(article_data, 1):
            print(f"Article {i}: {article['translated_title']}")
        analyze_repeated_words(article_data)
    
    finally:
        driver.quit()

def test_elpais_scraper(driver):
    """Test to scrape El Pais opinion articles"""
    try:
        # Visit El País homepage
        driver.get("https://elpais.com/")
        print("Navigated to homepage")

        # Handle cookie consent
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
        )
        time.sleep(1)  # Small delay for stability
        driver.find_element(By.ID, "didomi-notice-agree-button").click()
        print("Accepted cookies")

        # Navigate to Opinion section
        driver.find_element(By.LINK_TEXT, "Opinión").click()
        print("Clicked on Opinion section")

        # Wait for articles to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "c_t"))
        )
        print("Articles loaded")

        # Fetch article elements
        articles = driver.find_elements(By.CLASS_NAME, "c")[:10]
        article_data = []
        print(f"Found {len(articles)} articles")

        # Process articles
        for article in articles:
            try:
                # Extract title
                title_elem = article.find_element(By.CLASS_NAME, "c_t")
                title = title_elem.text.strip()
                if not title:
                    continue

                # Extract first paragraph if available
                try:
                    content_elem = article.find_element(By.CLASS_NAME, "c_d")
                    content = content_elem.text.strip()
                except:
                    content = "No article description"

                # Extract image if available
                image_url = None
                try:
                    image_elem = article.find_element(By.TAG_NAME, "img")
                    image_url = image_elem.get_attribute("src")
                except:
                    pass

                article_data.append({
                    "title": title,
                    "content": content,
                    "image_url": image_url
                })
                print(f"\nProcessed article: {title[:50]}...")

                if len(article_data) == 5:
                    break

            except Exception as e:
                print(f"Skipping an article due to error: {e}")
                continue

        # Print and download article details
        print("\nScraped Articles:")
        for i, article in enumerate(article_data, 1):
            print(f"\nArticle {i}:")
            print(f"Title (Spanish): {article['title']}")
            print(f"Content: {article['content'][:100]}...")
            
            if article["image_url"]:
                print(f"Image URL: {article['image_url']}")
                try:
                    response = requests.get(article["image_url"], stream=True)
                    if response.status_code == 200:
                        os.makedirs('downloads', exist_ok=True)
                        filename = f"downloads/{article['title'].replace(' ', '_')[:50]}.jpg"
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        print(f"Downloaded image as {filename}")
                except Exception as e:
                    print(f"Failed to download image: {e}")

        # Translate titles using RapidAPI
        print("\nTranslating titles...")
        for article in article_data:
            payload = {
                "from": "es",  # Spanish
                "to": "en",    # English
                "text": article["title"]
            }
            try:
                response = requests.post(TRANSLATE_URL, json=payload, headers=TRANSLATE_HEADERS)
                response.raise_for_status()  # Raise an error for bad status codes
                translated_text = response.json().get("trans", "Translation failed")
                article["translated_title"] = translated_text
                print(f"\nOriginal: {article['title']}")
                print(f"Translated: {translated_text}")
            except requests.exceptions.RequestException as e:
                print(f"Translation failed for '{article['title']}': {e}")
                article["translated_title"] = "Translation failed"
            except Exception as e:
                print(f"Unexpected error during translation: {e}")
                article["translated_title"] = "Translation failed"

        # Analyze repeated words
        all_words = []
        for article in article_data:
            if article["translated_title"] != "Translation failed":
                words = [word.lower() for word in article["translated_title"].split()]
                all_words.extend(words)

        word_counts = Counter(all_words)
        repeated_words = {word: count for word, count in word_counts.items() if count > 2}

        if repeated_words:
            print("\nWords repeated more than twice in translated headers:")
            for word, count in repeated_words.items():
                print(f"'{word}': {count} times")
        else:
            print("\nNo words repeated more than twice in translated headers.")

        # Assertions
        assert len(article_data) > 0, "No articles were processed"
        assert any(article["translated_title"] != "Translation failed" for article in article_data), "No translations succeeded"

    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    main()
