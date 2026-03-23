#!/usr/bin/env python3
"""Scrape KONTEXT:Wochenzeitung and generate an RSS feed."""

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import escape

import requests
from bs4 import BeautifulSoup


SITE_URL = "https://www.kontextwochenzeitung.de/"
FEED_TITLE = "KONTEXT:Wochenzeitung"
FEED_DESC = "Investigativer Regionaljournalismus aus Stuttgart/BW"


def scrape_articles():
    resp = requests.get(SITE_URL, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []
    seen_urls = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if not re.search(r"/\w+/\d+/[\w-]+-\d+\.html$", href):
            continue
        if "#comment" in href:
            continue
        url = href if href.startswith("http") else SITE_URL.rstrip("/") + href
        if url in seen_urls:
            continue
        seen_urls.add(url)
        title = link.get_text(strip=True)
        if len(title) < 5:
            continue
        article_el = link.find_parent(class_="article") or link.find_parent("div")
        category = ""
        teaser = ""
        pub_date = ""
        if article_el:
            cat_el = article_el.find(class_=re.compile(r"category|rubrik"))
            if cat_el:
                category = cat_el.get_text(strip=True)
            teaser_el = article_el.find(class_=re.compile(r"teaser|bodytext"))
            if teaser_el:
                teaser = teaser_el.get_text(strip=True)[:300]
            date_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", article_el.get_text())
            if date_match:
                try:
                    dt = datetime.strptime(date_match.group(1), "%d.%m.%Y")
                    pub_date = dt.strftime("%a, %d %b %Y 06:00:00 +0100")
                except ValueError:
                    pass
        articles.append({"title": title, "url": url, "category": category, "teaser": teaser, "pub_date": pub_date})
    return articles


def build_rss(articles):
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = FEED_TITLE
    ET.SubElement(channel, "link").text = SITE_URL
    ET.SubElement(channel, "description").text = FEED_DESC
    ET.SubElement(channel, "language").text = "de"
    ET.SubElement(channel, "lastBuildDate").text = now
    atom_link = ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", "https://tilian86.github.io/kontext-rss/feed.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")
    for article in articles:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article["title"]
        ET.SubElement(item, "link").text = article["url"]
        ET.SubElement(item, "guid").text = article["url"]
        desc = article["teaser"] if article["teaser"] else article["title"]
        ET.SubElement(item, "description").text = desc
        if article["category"]:
            ET.SubElement(item, "category").text = article["category"]
        if article["pub_date"]:
            ET.SubElement(item, "pubDate").text = article["pub_date"]
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    return ET.tostring(rss, encoding="unicode", xml_declaration=True)


def main():
    print("Scraping KONTEXT:Wochenzeitung...")
    articles = scrape_articles()
    print(f"Found {len(articles)} articles")
    rss_xml = build_rss(articles)
    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(rss_xml)
    print("RSS feed written to feed.xml")


if __name__ == "__main__":
    main()
