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


logger = logging.getLogger("SiteMap")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


def is_resource(url):
    file_extension = url.split(".")[-1]
    if file_extension in ["pdf", "jpg", "jpeg", "png", "gif", "bmp"]:
        return True
    return False


def is_deep_link(base_url, url):
    parsed_url = urlparse(url)
    parsed_nerloc = parsed_url.netloc.split(".")

    base_parsed_url = urlparse(base_url)
    base_netloc = base_parsed_url.netloc.split(
        ".")[1]  # ideally middle element

    return base_netloc in parsed_nerloc


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

        # If the "href" attribute exists, isn't a fragment identifier (#), isn't email specifier
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

    visualize_graph(_graph)


if __name__ == '__main__':
    main()
