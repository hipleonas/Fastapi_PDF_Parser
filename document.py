from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json, os

BASE_URL = "https://academy.fitstop.com"
LOGIN_URL = f"{BASE_URL}/users/sign_in"
USERNAME = "your_email@example.com"
PASSWORD = "your_password"
visited_urls = set()
crawled_data = []

def save_json():
    with open("fitstop_data.json", "w", encoding="utf-8") as f:
        json.dump(crawled_data, f, ensure_ascii=False, indent=2)

def extract_data(page, url):
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    content_text = soup.get_text(separator='\n')
    images = [urljoin(url, img['src']) for img in soup.find_all("img") if "src" in img.attrs]
    videos = [urljoin(url, video['src']) for video in soup.find_all("video") if "src" in video.attrs]

    # YouTube / embedded iframe
    iframes = [iframe['src'] for iframe in soup.find_all("iframe") if "youtube" in iframe.get("src", "")]
    videos += iframes

    return {
        "url": url,
        "text": content_text,
        "images": images,
        "videos": videos
    }

def crawl_course(page, url):
    if url in visited_urls:
        return
    visited_urls.add(url)
    
    print(f"[+] Crawling: {url}")
    page.goto(url)
    page.wait_for_timeout(2000)

    data = extract_data(page, url)
    crawled_data.append(data)

    soup = BeautifulSoup(page.content(), "html.parser")
    for a in soup.find_all("a", href=True):
        full_url = urljoin(url, a['href'])
        if BASE_URL in full_url and full_url not in visited_urls:
            crawl_course(page, full_url)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Go to login page
        page.goto(LOGIN_URL)
        page.fill('input[name="user[email]"]', USERNAME)
        page.fill('input[name="user[password]"]', PASSWORD)
        page.click('input[name="commit"]')
        page.wait_for_timeout(3000)

        # Start crawling course homepage
        crawl_course(page, f"{BASE_URL}/collections")

        browser.close()

    save_json()
    print("[✓] Done. Saved to fitstop_data.json")

if __name__ == "__main__":
    main()
