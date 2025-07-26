import json
import os
import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv
load_dotenv()
visited_url = set()
crawled_data = []

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
LOGIN_URL = f"{BASE_URL}/{USERNAME}/sign_in"

def extract_data(page, url):
    soup = BeautifulSoup(page.content(), "html.parser")
    text = soup.get_text(separator="\n")

    imgs = [urljoin(url, img["src"]) for img in soup.find_all("img") if "src" in img.attrs]
    vids = [urljoin(url, vid["src"]) for vid in soup.find_all("video") if "src" in vid.attrs]
    iframes = [iframe['src'] for iframe in soup.find_all("iframe") if "youtube" in iframe.get("src", "")]
    vids = vids + iframes
    return {
        "url": url,
        "text": text,
        "images": imgs,
        "videos": vids
    }
async def crawl_course(page, url):
    if url in visited_url:
        return
    visited_url.add(url)
    print(f"Crawling: {url}")


    try:
        await page.goto(url,timeout=0)

        content = await page.content()

        data = extract_data(content, url)

        crawled_data.append(data)
        soup = BeautifulSoup(content, "html.parser")


        for a in soup.find_all("a", href = True):
            full_url = urljoin(url, a["href"])
            if BASE_URL in full_url and full_url not in visited_url:
                await crawl_course(page, full_url)

    except Exception as e:
        print(f"Error crawling {url}: {e}")


def save_json():

    with open("crawled_data.json", "w", encoding = "utf-8") as f:
        json.dump(crawled_data, f , ensure_ascii=False, indent=2)
    print("Saved to crawled_data.json")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(BASE_URL, timeout=0)
        print("Open page success, you can now interact with the page")
        # await page.wait_for_selector('input[name="user[email]"]', timeout=30000)
        #Wait to fill in the form
        await page.wait_for_selector('input[name="username"]')
        await page.wait_for_selector('input[name="password"]')

        await page.fill('input[name="user[username]"]', USERNAME)
        await page.fill('input[name="user[password]"]', PASSWORD)

        await page.click('button[type="submit]')

        # await page.wait_for_load_state('networkidle')
        print('Login completed')
        # await crawl_course(page, BASE_URL)
        save_json()
        await browser.close() # giữ cho browser không bị đóng
        
 
asyncio.run(main())
