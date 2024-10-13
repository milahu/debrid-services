#!/usr/bin/env python3

import os
import re
import sys
import time
import json
import urllib.parse

# pypi modules
import requests
#from bs4 import BeautifulSoup



result_path = "debrid-hoster-map.json"



def get_netloc(url):
    netloc = urllib.parse.urlparse(url).netloc # "real-debrid.com"
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def get_debrid_html(debrid_url, debrid_id):
    debrid_cache = "cache/" + debrid_id + ".html"
    if os.path.exists(debrid_cache):
        # read cache
        with open(debrid_cache) as f:
            debrid_html = f.read()
    else:
        response = requests.get(debrid_url) # , **requests_get_kwargs)
        assert response.status_code == 200
        #response_status = response.response_status
        #print("response.status_code", response.status_code)
        #print("response.headers", response.headers)
        #print("response.text", response.text)
        #result = response.json()
        debrid_html = response.text
        # write cache
        with open(debrid_cache, "w") as f:
            f.write(debrid_html)
    return debrid_html



# result
debrid_hoster_map = dict()



# note: we must be logged in to see this page
# otherwise we get "403 - forbidden"
# (idiots just love to hide...)
debrid_url = "https://real-debrid.com/compare"
debrid_id = get_netloc(debrid_url)
debrid_html = get_debrid_html(debrid_url, debrid_id)
debrid_hoster_map[debrid_id] = dict()
regex = (
    r'<img src="https://fcdn.real-debrid.com/0830/images/hosters/100_100/([^"]+).png" ' +
    r'height="42" width="42" alt="[^"]+" title="([^"]+)"'
)
for match in re.finditer(regex, debrid_html):
    hoster_id, hoster_urls = match.groups()
    hoster_urls = hoster_urls.split(",")
    if hoster_id in debrid_hoster_map[debrid_id]:
        raise KeyError(f"key already exists: {hoster_id!r}")
    debrid_hoster_map[debrid_id][hoster_id] = hoster_urls



debrid_url = "https://www.deepbrid.com/status"
debrid_id = get_netloc(debrid_url)
debrid_html = get_debrid_html(debrid_url, debrid_id)
debrid_hoster_map[debrid_id] = dict()
#regex = r'<tr><td class="border-b"><div class="hosters ([^ "]+)">' # free hosters
regex = r'\n<td class="border-b"><div class="hosters ([^ "]+)"></div>' # premium hosters
for match in re.finditer(regex, debrid_html):
    hoster_id = match.group(1)
    if hoster_id in debrid_hoster_map[debrid_id]:
        raise KeyError(f"key already exists: {hoster_id!r}")
    debrid_hoster_map[debrid_id][hoster_id] = True




debrid_url = "https://alldebrid.com/hosts/"
debrid_id = get_netloc(debrid_url)
debrid_html = get_debrid_html(debrid_url, debrid_id)
debrid_hoster_map[debrid_id] = dict()
regex = r'<a href="/hosts/([^ "]+)/">' # premium hosters
for match in re.finditer(regex, debrid_html):
    hoster_id = match.group(1)
    if hoster_id in debrid_hoster_map[debrid_id]:
        raise KeyError(f"key already exists: {hoster_id!r}")
    debrid_hoster_map[debrid_id][hoster_id] = True



debrid_url = "https://support.torbox.app/en/articles/9837721-supported-debrid-hosters"
debrid_id = "torbox.app"
debrid_html = get_debrid_html(debrid_url, debrid_id)
debrid_hoster_map[debrid_id] = dict()
# sections of supported hosters
regex1 = r'<h2 id="[^"]+">Supported (File|Streaming) Hosters</h2>(.*?)(?=<h2|<section)'
regex2 = r'href="(http[^"]+)"'
for match1 in re.finditer(regex1, debrid_html):
    section_type, section_html = match1.groups()
    for match2 in re.finditer(regex2, section_html):
        hoster_url = match2.group(1)
        hoster_id = get_netloc(hoster_url)
        if hoster_id in debrid_hoster_map[debrid_id]:
            raise KeyError(f"key already exists: {hoster_id!r}")
        debrid_hoster_map[debrid_id][hoster_id] = True



debrid_url = "https://www.premiumize.me/services?q=all"
debrid_id = get_netloc(debrid_url)
debrid_html = get_debrid_html(debrid_url, debrid_id)
debrid_hoster_map[debrid_id] = dict()
# src="https://www.google.com/s2/favicons?domain=uploadgig.com"
regex = r'src="https://www\.google\.com/s2/favicons\?domain=([^"]+)"'
for match in re.finditer(regex, debrid_html):
    hoster_id = match.group(1)
    if hoster_id in debrid_hoster_map[debrid_id]:
        raise KeyError(f"key already exists: {hoster_id!r}")
    debrid_hoster_map[debrid_id][hoster_id] = True



# sort by debrid_id
debrid_hoster_map = dict(sorted(debrid_hoster_map.items()))

# sort by hoster_id
for debrid_id in debrid_hoster_map:
    debrid_hoster_map[debrid_id] = dict(sorted(debrid_hoster_map[debrid_id].items()))



print("writing", result_path)
with open(result_path, "w") as f:
    json.dump(debrid_hoster_map, f, indent=2)
