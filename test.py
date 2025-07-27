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

def extract_data(content, url):
    soup = BeautifulSoup(content, "html.parser")
    """1. Trích xuất văn bản"""
    text = soup.get_text(separator = "\n")
    """2. Trích xuấy hình ảnh"""

    imgs = []
    for img in soup.find_all("img"):
        if "src" in img.attrs:
            imgs.append(urljoin(url, img["src"]))
        if "data-src" in img.attrs:
            imgs.append(urljoin(url, img["data-src"]))
    
    videos = []

    """3. Trích xuất video"""
    #Trường hợp 1: video có với <a> chứa liên kết video
    for video in soup.find_all("a", href = True):
        href = video["href"]
        if any(keyword in href for keyword in ["youtube.com/watch", "vimeo.com/", ".mp4", ".webm", ".mov"]):
            videos.append(urljoin(url, href))
    #Trường hợp 2: video có với <video> chứa liên kết video
    for vid in soup.find_all("video"):
        if "src" in vid.attrs:
            videos.append(urljoin(url,vid["src"]))
        for source in vid.find_all("source"):
            if "src" in source.attrs:
                videos.append(urljoin(url, source["src"]))
        if "poster" in vid.attrs:
            imgs.append(urljoin(url, vid["poster"]))
    
    for iframe in soup.find_all("iframe"):
        if "src" in iframe.attrs:
            iframe_src = iframe["src"]
            if any(domain in iframe_src for domain in ["youtube.com", "vimeo.com", "dailymotion.com"]):
                videos.append(urljoin(url, iframe_src))

    # Xử lý lazy loading và các thuộc tính data-*
    for tag in soup.find_all(lambda tag: any(attr in tag.attrs for attr in ["data-src", "data-video-url", "data-href"])):
        if "data-src" in tag.attrs and any(ext in tag["data-src"] for ext in [".mp4", ".webm", ".mov"]):
            videos.append(urljoin(url, tag["data-src"]))
        if "data-video-url" in tag.attrs:
            videos.append(urljoin(url, tag["data-video-url"]))
        if "data-href" in tag.attrs and any(domain in tag["data-href"] for domain in ["youtube.com", "vimeo.com"]):
            videos.append(urljoin(url, tag["data-href"]))
    
    for div in soup.find_all("div", attrs={"data-thumb": True}):
        thumb_url = div["data-thumb"]
        if "vimeocdn.com" in thumb_url:
            # Thêm thumbnail vào danh sách hình ảnh
            imgs.append(urljoin(url, thumb_url))
            
            # Cố gắng trích xuất ID video Vimeo từ URL thumbnail
            if "/video/" in thumb_url:
                video_id = thumb_url.split("/video/")[1].split("-")[0]
                videos.append(f"https://vimeo.com/{video_id}")

    # Xử lý các div có background-image chứa video thumbnail
    for div in soup.find_all("div", style=True):
        style = div["style"]
        if "background-image:" in style and "vimeocdn.com" in style:
            # Trích xuất URL từ chuỗi style
            start = style.find("url(") + 4
            end = style.find(")", start)
            img_url = style[start:end].strip('"\'')

            imgs.append(urljoin(url, img_url))
            
            # Nếu có thể trích xuất ID video
            if "/video/" in img_url:
                video_id = img_url.split("/video/")[1].split("-")[0]
                videos.append(f"https://vimeo.com/{video_id}")
    videos = list(set(videos))  # Loại bỏ trùng lặp
    return {
        "url": url,
        "text":text,
        "imgs":imgs,
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
        for link_idx,link in enumerate(course_links):
            if link_idx == 1:
                return    
            course_data = {
                 "course_info": {},
                "activities": []
            }
            full_url = urljoin(BASE_URL, link)
            if full_url not in visited_url and not any(ignore in full_url for ignore in ignore_paths):
                visited_url.add(full_url)
                print(f"Crawling course: {full_url}")
                try:
                    await page.goto(full_url, wait_until='networkidle', timeout=TIMEOUT)
                    html = await page.content()
                    course_info = extract_data(html, full_url)
                    course_data["course_info"] = course_info
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
                           
                                course_data["activities"].append(activity_data)

                                await page.go_back(wait_until='networkidle')
                                await page.wait_for_load_state('networkidle', timeout=TIMEOUT)
                            except Exception as e:
                                print(f"Error crawling activity {full_act_url}: {e}")
                                continue

                    await page.go_back(wait_until = 'networkidle')
                    await page.wait_for_load_state('networkidle', timeout = TIMEOUT)

                    """================================================="""
                    # save_json()
                    await page.go_back(wait_until='networkidle')
                    await page.wait_for_load_state('networkidle', timeout=TIMEOUT)
                except Exception as e:
                    print(f"Error crawling course {full_url}: {e}")
                    continue
            crawled_data.append(course_data)
            save_json()
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