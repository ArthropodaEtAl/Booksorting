import os
import requests
from urllib.parse import quote
import pprint

from lxml import html
import rapidfuzz
import pandas as pd


def url_maker(input_title):
    query = quote(f"{input_title}")
    url = f"https://app.thestorygraph.com/browse?search_term={query}"
    return url


def url_maker_with_author(input_title, input_author):
    query = quote(f"{input_author} {input_title}")
    url = f"https://app.thestorygraph.com/browse?search_term={query}"
    return url


def format_author_title(info):
    return " - ".join(info)


def get_matches(input_title, input_author):
    def get_results_from_url(url):
        response = requests.get(url)
        tree = html.fromstring(response.content)
        book_cards = tree.xpath('//span[contains(@class, "search-results-books-panes")]/div')
        results = {}
        for i, card in enumerate(book_cards):
            info = []

            book_link = card.xpath(".//h1/a")[0]
            title = book_link.text
            link = book_link.get("href")
            info.append(title)

            author = None
            try:
                author_p = card.xpath('.//p[contains(@class, "font-body")]/a')[0]
                author = author_p.text
                if author:
                    info.append(author)
            except:
                pass

            isbn_e = card.xpath('.//div[contains(@class, "edition-info")]/p')[0]
            isbn = "".join(isbn_e.itertext()).split(" ")[-1]
            results[format_author_title(info)] = [title, author, link, isbn]
        return results

    results = get_results_from_url(url_maker(input_title))
    result_with_author = get_results_from_url(url_maker_with_author(input_title, input_author))
    results.update(result_with_author)

    # find best match
    matches = rapidfuzz.process.extract(
        format_author_title([input_title, input_author]), results.keys()
    )
    try:
        best_match, score, _ = matches[0]
    except:
        print(results)
    try:
        relative_score = matches[0][1] - matches[1][1]
    except:
        relative_score = 100
    try:
        match_data = results[best_match]
        match_data.append(score)
        match_data.append(relative_score)
    except:
        match_data = ["Error"] * 6
    return match_data


df = pd.read_csv("Cleaned_list.csv", encoding="utf-8")
New_data = []

for index, row in df.iterrows():
    the_match = get_matches(row["Title"], row["Author"])
    New_data.append(the_match)

match_list = pd.DataFrame(
    New_data,
    columns=["Match Title", "Match_Author", "Link", "Match_ISBN", "Score", "Relative"],
)
df = df.join(match_list)
df.to_csv("Cleaned_matched_list_2.csv")
df.to_excel("Cleaned_matched_list_2.xlsx")


input_author = "roger"
input_title = "lord of light"

input_author = "abi umeda"
input_title = "children of the whales vol 4"

input_author = "Malcom Lyons"
input_title = "The Arabian Nights Volume 1"

# query = quote(f'{input_author} {input_title}')
