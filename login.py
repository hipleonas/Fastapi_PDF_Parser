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
TIMEOUT = 30000
# LOGIN_URL = f"{BASE_URL}/sign_in"

# def extract_data(content, url):
#     soup = BeautifulSoup(content, "html.parser")
#     text = soup.get_text(separator="\n")
#     imgs = [urljoin(url, img["src"]) for img in soup.find_all("img") if "src" in img.attrs]
#     vids = [urljoin(url, vid["src"]) for vid in soup.find_all("video") if "src" in vid.attrs]
#     iframes = [iframe['src'] for iframe in soup.find_all("iframe") if "youtube" in iframe.get("src", "")]
#     vids = vids + iframes
#     return {
#         "url": url,
#         "text": text,
#         "images": imgs,
#         "videos": vids
#     }
def extract_data(content, url):
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text(separator = "\n")
    imgs = []
    for img in soup.find_all("img"):
        if "src" in img.attrs:
            imgs.append(urljoin(url, img["src"]))
    videos = []

    for vid in soup.find_all("video"):
        if "src" in vid.attrs:
            videos.append(urljoin(url, vid["src"]))

        for source in vid.find_all("source"):
            if "src" in source.attrs:
                videos.append(urljoin(url, source["src"]))
    #Extract iframe
    for iframe in soup.find_all("iframe"):
        iframe_src = iframe["src"]
        if "youtube.com" in iframe_src or \
               "player.vimeo.com" in iframe_src or \
               "dailymotion.com" in iframe_src or \
               "facebook.com/plugins/video.php" in iframe_src:
                videos.append(urljoin(url, iframe_src))
        elif not any(keyword in iframe_src for keyword in ["ads", "ad-placement", "googlead"]):
            videos.append(urljoin(url, iframe_src))

    videos = list(set(videos))
    #Extract tags suitable for lazy loading

    for tag in soup.find_all(lambda tag: tag.has_attr('data-src') or tag.has_attr('data-video-url') or tag.has_attr('data-href')):
        if "data-src" in tag.attrs:
            videos.append(urljoin(url, tag["data-src"]))
        elif "data-video-url" in tag.attrs:
            videos.append(urljoin(url, tag["data-video-url"]))
        elif 'data-href' in tag.attrs and ("youtube.com" in tag['data-href'] or "vimeo.com" in tag['data-href']):
            videos.append(urljoin(url, tag['data-href']))            
    return {
        "url": url,
        "text": text,
        "images": imgs,
        "videos": videos
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
async def get_activities_links(page):
    try:
        activity_links = await page.evaluate('''()=>{
            const elements = document.querySelectorAll('a[href*="/activities/"]');
            return Array.from(elements).map(el => el.getAttribute('href'));
        }''')
        return [link for link in activity_links if link.startswith("/activities/")]
    except Exception as e:
        print(f"Error getting activities links: {e}")
        return []

async def crawl_course(page, url):
    if url in visited_url:
        return
    visited_url.add(url)
    print(f"Crawling: {url}")
    try:
        await page.goto(url, wait_until='networkidle', timeout=TIMEOUT)
        await page.wait_for_load_state('networkidle', timeout=TIMEOUT)

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
                    await page.goto(full_url, wait_until='networkidle', timeout=TIMEOUT)
                    html = await page.content()
                    course_data = extract_data(html, full_url)
                    crawled_data.append(course_data)
                    """
                    We will write all of the course activities over here
                    """
                    act_links = await get_activities_links(page)

                    for act_link in act_links:
                        full_act_url = urljoin(full_url, act_link)

                        if full_act_url not in visited_url and not any(ignore in full_act_url for ignore in ignore_paths):
                            visited_url.add(full_act_url)
                            try:
                                await page.goto(full_act_url, wait_until='networkidle', timeout=TIMEOUT)
                                html = await page.content()
                                activity_data = extract_data(html,full_url)
                                crawled_data.append(activity_data)
                                save_json()

                                await page.go_back(wait_until='networkidle')
                                await page.wait_for_load_state('networkidle', timeout=TIMEOUT)
                            except Exception as e:
                                print(f"Error crawling activity {full_act_url}: {e}")
                                continue


                    save_json()
                    await page.go_back(wait_until = 'networkidle')
                    await page.wait_for_load_state('networkidle', timeout = TIMEOUT)

                    """================================================="""
                    save_json()
                    await page.go_back(wait_until='networkidle')
                    await page.wait_for_load_state('networkidle', timeout=TIMEOUT)
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
        await page.goto(BASE_URL, wait_until='networkidle', timeout=TIMEOUT)
        print("Open login page success")

        await page.locator('input[name="username"]').fill(USERNAME)
        await page.locator('input[name="password"]').fill(PASSWORD)
        await page.locator('button[type="submit"]').click()
        await page.wait_for_load_state('networkidle', timeout=TIMEOUT)
        print('Login completed')

        await context.storage_state(path="auth.json")  # Lưu phiên đăng nhập
        await crawl_course(page, BASE_URL)
        await browser.close()

asyncio.run(main())