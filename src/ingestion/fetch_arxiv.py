import urllib.request

url = "http://export.arxiv.org/api/query?search_query=all:physics&max_results=3"

try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    response = urllib.request.urlopen(req)
    print(response.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("Status:", e.code)
    print("Body:", e.read().decode("utf-8", errors="replace"))