import json
import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()

visited_url = set()
crawled_data = []
ignore_paths = ["/notifications", "/history", "/logout", "/profile", "/settings", "/contact"]
BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
# LOGIN_URL = f"{BASE_URL}/sign_in"

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

async def get_course_links(page):
    try:
        # Sử dụng JavaScript để lấy tất cả các link khóa học
        links = await page.evaluate('''() => {
            const elements = document.querySelectorAll('a[href*="/courses/"]');
            return Array.from(elements).map(el => el.getAttribute('href'));
        }''')
        return [link for link in links if link and link.startswith("/courses/")]
    except Exception as e:
        print(f"Error getting course links: {e}")
        return []

async def crawl_course(page, url):
    if url in visited_url:
        return
    visited_url.add(url)
    print(f"Crawling: {url}")

    try:
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_load_state('networkidle', timeout=30000)

        # Lấy danh sách link khóa học
        course_links = await get_course_links(page)
        #./course/code
        print(f"Found {len(course_links)} course links")

        for link in course_links:
            full_url = urljoin(BASE_URL, link)
            if full_url not in visited_url and not any(ignore in full_url for ignore in ignore_paths):
                visited_url.add(full_url)
                print(f"Crawling course: {full_url}")
                try:
                    await page.goto(full_url, wait_until='networkidle', timeout=30000)
                    html = await page.content()
                    course_data = extract_data(html, full_url)
                    crawled_data.append(course_data)
                    save_json()
                    await page.go_back(wait_until='networkidle')
                    await page.wait_for_load_state('networkidle', timeout=30000)
                except Exception as e:
                    print(f"Error crawling course {full_url}: {e}")
                    continue

    except Exception as e:
        print(f"Error crawling {url}: {e}")

def save_json():
    with open("crawled_data.json", "w", encoding="utf-8") as f:
        json.dump(crawled_data, f, ensure_ascii=False, indent=2)
    print("Saved to crawled_data.json")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
        print("Open login page success")

        await page.locator('input[name="username"]').fill(USERNAME)
        await page.locator('input[name="password"]').fill(PASSWORD)
        await page.locator('button[type="submit"]').click()
        await page.wait_for_load_state('networkidle', timeout=30000)
        print('Login completed')

        await context.storage_state(path="auth.json")  # Lưu phiên đăng nhập
        await crawl_course(page, BASE_URL)
        await browser.close()

asyncio.run(main())