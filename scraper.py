
import requests, time, random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import undetected_chromedriver as uc

#----------SNIPPET-------------
def make_snippet(text, keyword, length=160):
    text = text.replace("\n", " ").strip()

    idx = text.lower().find(keyword.lower())
    if idx == -1:
        return text[:length] + "..."

    start = max(idx - 60, 0)
    return "..." + text[start:start + length] + "..."


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
    random_delay(2, 4)    
    driver.get(url)

    random_delay(2, 4)
    html = driver.page_source
    driver.quit()

    return html


# ---------- EXTRACT TEXT + LINKS ----------
def extract_data(html, keyword, url):
    soup = BeautifulSoup(html, "html.parser")

    results = []
    seen_snippets = set()

    page_title = soup.title.string.strip() if soup.title else url

    for tag in soup.find_all(["p", "li", "h3", "a"]):
        text = tag.get_text(" ", strip=True)

        if not any(word in text.lower() for word in keyword.lower().split()):
            continue

        if len(text) < 40:
            continue

        snippet = make_snippet(text, keyword)

        unique_key = snippet + url
        if unique_key in seen_snippets:
            continue

        seen_snippets.add(unique_key)

        results.append({
            "title": page_title,
            "snippet": snippet,
            "url": url
        })

    return results



# ---------- MAIN CRAWLER ----------
def crawl(start_url, keyword, max_depth=1, max_pages=10):
    domain = urlparse(start_url).netloc
    visited = set([start_url])
    pages_crawled = 0
    queue = deque([(start_url, 0)])
      # prevents duplicate search results

    results = []

    while queue:
        url, depth = queue.popleft()
        visited.add(url)
        if depth > max_depth or pages_crawled >= max_pages:
            continue

        html = static_scrape(url)
        if not html:
            html = dynamic_scrape(url)

        if not html:
            continue
        pages_crawled += 1

        page_results = extract_data(html, keyword, url) or []
        results.extend(page_results)

        # 🔹 THIS IS ONLY FOR DISCOVERING NEW PAGES
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])

            if urlparse(link).netloc == domain and link not in visited:
                queue.append((link, depth + 1))

    return results