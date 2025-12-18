from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

app = Flask(__name__)

def crawl_and_search(start_url, keyword, max_depth, max_pages):
    visited = set()
    pages_visited = 0
    queue = deque([(start_url, 0)])
    results = []

    domain = urlparse(start_url).netloc

    while queue:
        if pages_visited >= max_pages:
            break

        url, depth = queue.popleft()

        if depth > max_depth or url in visited:
            continue

        visited.add(url)

        try:
            response = requests.get(url, timeout=8)
            soup = BeautifulSoup(response.text, "html.parser")
            pages_visited += 1
        except:
            continue

        # Extract text containing keyword
        for tag in soup.find_all(["p", "li"]):
            text = tag.get_text(strip=True)
            if keyword.lower() in text.lower() and len(text) > 50:
                results.append({
                    "text": text,
                    "source": url
                })

        # Crawl links
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            if (
                urlparse(link).netloc == domain
                and link not in visited
            ):
                queue.append((link, depth + 1))

    return results


@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    if request.method == "POST":
        start_url = request.form["url"]
        keyword = request.form["keyword"]
        depth = int(request.form["depth"])

        max_pages = int(request.form["max_pages"])

        results = crawl_and_search(start_url, keyword, depth, max_pages)


    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
