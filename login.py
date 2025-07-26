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
def get_all_links(content, url):
    soup = BeautifulSoup(content, "html.parser")
    to_links = []
    for tag in soup.find_all(attrs={"to": True}):
        print(tag)
    #     link = tag.get("to")
    #     print(link)
    #     if link and link.startswith("/courses/"):
    #         to_links.append(link)
    return to_links
async def crawl_course(page, url):
    if url in visited_url:
        return
    visited_url.add(url)
    # print(f"Crawling: {url}")


    try: 
        print(f"Visiting {url}")
        await page.goto(url,timeout=0)

        await page.wait_for_selector('course-card-cover')

        # Lấy các link từ attribute `to`
        elements = await page.query_selector_all('course-card-cover')
        for elem in elements:
            to_attr = await elem.get_attribute('to')
            # print("Found TO:", to_attr)
            if to_attr and to_attr.startswith("/courses/"):
                full_url = f"https://www.classcentral.com{to_attr}"
                # lưu hoặc xử lý link
                print(full_url)
                data = extract_data(await page.content(), full_url)
                crawled_data.append(data)
        

        # content = await page.content()
        # # Check if the URL is in the ignore list
        # # parsed_url = urlparse(url)
        # #Trích xuất taart cả các links
        # links = get_all_links(content, url)
        # print(links)

        # for link in links:
        #     data = extract_data(content, link)
        #     crawled_data.append(data)


        # if not any(ignore in parsed_url.path for ignore in ignore_paths):
        #     data = extract_data(content, url)
        #     crawled_data.append(data)
        # data = extract_data(content, url)

        # crawled_data.append(data)

        # soup = BeautifulSoup(content, "html.parser")


        # for a in soup.find_all("a", href = True):
        #     full_url = urljoin(url, a["href"])
        #     parsed_full = urlparse(full_url)

        #     if BASE_URL in full_url and full_url not in visited_url  and not any(ignore in parsed_full.path for ignore in ignore_paths):
        #         await crawl_course(page, full_url)

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
        await page.locator('input[name="username"]').fill(USERNAME)
        await page.locator('input[name="password"]').fill(PASSWORD)

        # Nhấn nút login
        await page.locator('button[type="submit"]').click()

        # await page.wait_for_load_state('networkidle')
        print('Login completed')
        await crawl_course(page, BASE_URL)
        save_json()
        await browser.close() # giữ cho browser không bị đóng
        
 
asyncio.run(main())
