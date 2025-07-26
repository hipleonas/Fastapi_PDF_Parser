import json
import os
import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv
import requests
load_dotenv()
visited_url = set()
crawled_data = []
ignore_paths = ["/notifications", "/history", "/logout","/profile","/settings", "/contact"]
BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
LOGIN_URL = f"{BASE_URL}/{USERNAME}/sign_in"

def extract_data(content, url):
    soup = BeautifulSoup(content, "html.parser")
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

    try: 
        # print(f"Visiting {url}")
        # await page.goto(url,timeout=0)
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_selector('course-card-cover', timeout=10000)

        # await page.wait_for_selector('course-card-cover', timeout = 10000)
    
        # Lấy các link từ attribute `to`
        elements = await page.query_selector_all('course-card-cover')
        for elem in elements:
            to_attr = await elem.get_attribute('to')
            print("Found TO:", to_attr)
            if to_attr and to_attr.startswith("/courses/"):
                full_url = urljoin(BASE_URL, to_attr)
                if full_url not in visited_url:
                    visited_url.add(full_url)
                    await page.goto(full_url, wait_until='networkidle', timeout=30000)
                    html = await page.content()
                    course_data = extract_data(html, full_url)
                    crawled_data.append(course_data)
                    # save_json()
                    await page.go_back(wait_until='networkidle')
                    await page.wait_for_load_state('networkidle', timeout=30000)
            # if to_attr and to_attr.startswith("/courses/"):
            #     full_url = urljoin(BASE_URL, f"fitstop{to_attr}")
            #     # lưu hoặc xử lý link
            #     print(full_url)
                # if full_url not in visited_url:
                #     visited_url.add(full_url)
                #     await page.goto(full_url, timeout = 0)
                #     html = await page.content()
                #     # print(html)
                #     course_data = extract_data(html, full_url)
                #     crawled_data.append(course_data)
                #     await page.go_back()
    except Exception as e:
        print(f"Error crawling {url}: {e}")


def save_json():

    with open("crawled_data.json", "w", encoding = "utf-8") as f:
        json.dump(crawled_data, f , ensure_ascii=False, indent=2)
    print("Saved to crawled_data.json")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        page = await context.new_page()
        await page.goto(BASE_URL, wait_until='networkidle',timeout=30000)
        print("Open page success, you can now interact with the page")
        # await page.wait_for_selector('input[name="user[email]"]', timeout=30000)
        #Wait to fill in the form
        await page.locator('input[name="username"]').fill(USERNAME)
        await page.locator('input[name="password"]').fill(PASSWORD)
        await page.locator('button[type="submit"]').click()
        await page.wait_for_load_state('networkidle')

        # await page.wait_for_load_state('networkidle')
        print('Login completed')
        await context.storage_state(path="auth.json")


        await crawl_course(page, BASE_URL)
        save_json()
        await browser.close() # giữ cho browser không bị đóng
        
 
asyncio.run(main())
