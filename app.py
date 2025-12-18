from flask import Flask, render_template, request
from scraper import crawl

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    if request.method == "POST":
        url = request.form["url"]
        keyword = request.form["keyword"]
        depth = int(request.form["depth"])
        max_pages = int(request.form["max_pages"])

        results = crawl(url, keyword, depth, max_pages)

    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
