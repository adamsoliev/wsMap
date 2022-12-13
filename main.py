#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin
from urllib.parse import urlparse
import networkx as nx
import matplotlib.pyplot as plt


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


"""
def extract_urls(url):
  logger.debug(f"Processing {url}")
  # make a GET request to the specified URL
  response = requests.get(url)

  # parse the HTML content of the response
  soup = BeautifulSoup(response.content, 'html.parser')

  # extract all anchor tags from the HTML
  anchor_tags = soup.find_all('a')

  # extract the URLs from the anchor tags
  urls = [tag['href'] for tag in anchor_tags]

  # remove URLs that do not belong to the input URL
  base_url = url.split('/')[0] + '//' + url.split('/')[2]
  urls = [u for u in urls if u.startswith(base_url)]

  # recursively extract URLs from the URLs that were just extracted
  for sub_url in urls:
    # make sure the URL is a valid URL and not just a fragment or something else
    if sub_url.startswith('http'):
      extract_urls(sub_url)
"""

# create logger with 'spam_application'
logger = logging.getLogger("SiteMap")
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)


def is_resource(url):
    """
    # Check if URL is valid using a regular expression
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if regex.match(url) is None:
        return False
    """
    # Check if URL is a resource (e.g. PDF or image) using the file extension
    file_extension = url.split(".")[-1]
    if file_extension in ["pdf", "jpg", "jpeg", "png", "gif", "bmp"]:
        return True

    return False


def is_deep_link(base_url, url):
    parsed_url = urlparse(url)
    parsed_nerloc = parsed_url.netloc.split(".")

    base_parsed_url = urlparse(base_url)
    base_netloc = base_parsed_url.netloc.split(".")[1]

    return base_netloc in parsed_nerloc


def belongs_to_base_url(url, base_url):
    # Parse the passed URL and base URL
    parsed_url = urlparse(url)
    print("parsed_url.scheme: ", parsed_url.scheme)
    print("parsed_url.hostname: ", parsed_url.hostname)
    print("parsed_url.port: ", parsed_url.port)

    parsed_base_url = urlparse(base_url)
    print("parsed_base_url.scheme: ", parsed_url.scheme)
    print("parsed_base_url.hostname: ", parsed_url.hostname)
    print("parsed_base_url.port: ", parsed_url.port)

    # Check if the scheme, hostname, and port of the passed URL match the
    # scheme, hostname, and port of the passed base URL
    return (parsed_url.scheme == parsed_base_url.scheme and
            parsed_url.hostname == parsed_base_url.hostname and
            parsed_url.port == parsed_base_url.port)


_graph = {}


def extract_urls(root_url, base_url, visited_urls=[]):
    print(len(visited_urls))
    if (len(visited_urls) > 20):
        return [] 

    logger.debug(f"Processing {base_url}")
    response = requests.get(base_url)

    if (response.status_code != 200):
        logger.error(
            f"Request to {base_url} failed with status code {response.status_code}")
        return []

    extracted_urls = []

    soup = BeautifulSoup(response.text, "html.parser")
    logger.debug(f"Parsed {base_url}")

    for a in soup.find_all("a"):
        link = a.get("href")

        # If the "href" attribute exists and is not a fragment identifier (#)
        if link and not link.startswith("#") and not link.startswith("mailto"):
            # If relative make it abs
            if not link.startswith("http"):
                link = urljoin(base_url, link)

            # If the extracted URL has not been visited yet
            if link not in visited_urls and is_deep_link(root_url, link) and not is_resource(link):

                if base_url not in _graph:
                    _graph[base_url] = set()
                _graph[base_url].add(link)

                visited_urls.append(link)

                logger.info(f"Processed {link}")

                # Add the extracted URL to the list
                extracted_urls.append(link)

                # Recursively extract URLs from the extracted URL
                logger.debug(f"Recursing {link}")
                extracted_urls.extend(extract_urls(
                    root_url, link, visited_urls))

    return extracted_urls


def visualize_graph(graph):
    # Create a networkx graph from the given graph
    G = nx.Graph(graph)

    # Draw the graph using the spring layout
    pos = nx.spring_layout(G)
    nx.draw(G, pos)

    # Show the graph
    plt.show()


def main():

    url = 'https://twitter.com'
    extracted_urls = extract_urls(url, url)
    sorted(extracted_urls, key=len)
    print(*extracted_urls, sep='\n')

    """
    graph = {
        "A": ["B", "C"],
        "B": ["A", "D"],
        "C": ["A", "D"],
        "D": ["B", "C"]
    }

    visualize_graph(graph)
    """

    visualize_graph(_graph)


if __name__ == '__main__':
    main()
