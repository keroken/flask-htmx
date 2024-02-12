import jinja_partials
import feedparser
from flask import Flask, render_template, abort, request, redirect

feeds = {
  "https://blog.teclado.com/rss":
    {
      "title": "The Teclad Blog",
      "href": "https://blog.teclado.com/rss",
      "show_images": True,
      "entries": {}
    },
  "https://www.joshwcomeau.com/rss.xml":
    {
      "title": "Josh W. Comeau",
      "href": "https://www.joshwcomeau.com/rss.xml",
      "show_image": False,
      "entries": {}
    },
}

def create_app():
  app = Flask(__name__)
  jinja_partials.register_extensions(app)

  @app.route("/")
  @app.route("/feed/<path:feed_url>")
  def render_feed(feed_url: str = None):
    for url, feed_ in feeds.items():
      parsed_feed = feedparser.parse(url)
      for entry in parsed_feed.entries:
        if entry.link not in feed_["entries"]:
          feed_["entries"][entry.link] = {**entry, "read": False}

    if feed_url is None:
      feed = list(feeds.values())[0]
    else:
      feed = feeds[feed_url]

    return render_template("feed.html", feed=feed, entries=feed["entries"].values(), feeds=feeds)
  
  @app.route("/entries/<path:feed_url>")
  def render_feed_entries(feed_url: str):
    try:
      feed = feeds[feed_url]
    except KeyError:
      abort(400)

    page = int(request.args.get("page", 0))

    return render_template("partials/entry_page.html",
      entries=list(feed["entries"].values())[page*5:page*5+5],
      href=feed_url,
      page=page,
      max_page=len(feed["entries"])//5
    )

  @app.route("/feed/<path:feed_url>/entry/<path:entry_url>")
  def read_entry(feed_url: str, entry_url: str):
    feed = feeds[feed_url]
    entry = feed["entries"][entry_url]
    entry["read"] = True
    return redirect(entry_url)

  return app