import requests, time, random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import undetected_chromedriver as uc

# ---------- BOT AVOIDANCE ----------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/142 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/142 Safari/537.36"
]

def random_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))


# ---------- STATIC SCRAPER ----------
def static_scrape(url):
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9"
        }
        random_delay()
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.text
    except:
        return None


# ---------- DYNAMIC SCRAPER ----------
def dynamic_scrape(url):
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    driver = uc.Chrome(options=options)
    driver.get(url)

    random_delay(2, 4)
    html = driver.page_source
    driver.quit()

    return html


# ---------- EXTRACT TEXT + LINKS ----------
def extract_data(html, keyword, base_url):
    soup = BeautifulSoup(html, "html.parser")

    texts = []
    links = []

    for tag in soup.find_all(["p", "li", "span"]):
        text = tag.get_text(strip=True)
        if keyword.lower() in text.lower() and len(text) > 40:
            texts.append(text)

    for a in soup.find_all("a", href=True):
        link_text = a.get_text(strip=True)
        href = urljoin(base_url, a["href"])
        if keyword.lower() in link_text.lower():
            links.append(href)

    return texts, links


# ---------- MAIN CRAWLER ----------
def crawl(start_url, keyword, max_depth=1, max_pages=10):
    domain = urlparse(start_url).netloc
    visited = set([start_url])
    pages_crawled = 0
    queue = deque([(start_url, 0)])
    results = []

    while queue:
        url, depth = queue.popleft()
        if depth > max_depth or pages_crawled >= max_pages:
            continue

        html = static_scrape(url)
        if not html:
            html = dynamic_scrape(url)

        if not html:
            continue

        texts, links = extract_data(html, keyword, url)

        for t in texts:
            results.append({"url": url, "text": t})

        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            full_url = urljoin(url, a["href"])
            if urlparse(full_url).netloc == domain and full_url not in visited:
                visited.add(full_url)
                pages_crawled += 1
                queue.append((full_url, depth + 1))

    return results
