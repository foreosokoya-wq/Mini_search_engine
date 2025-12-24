from flask import Flask, render_template, request
from scraper import crawl

app = Flask(__name__)

@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    results = []

    if request.method == "POST":
        url = request.form["url"]
        keyword = request.form["keyword"]
        depth = int(request.form["depth"])
        max_pages = int(request.form["max_pages"])

        results = crawl(url, keyword, depth, max_pages)

    return render_template("index.html", results=results)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
