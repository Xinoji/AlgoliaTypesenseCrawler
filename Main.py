from parsel import Selector
from urllib.parse import urljoin
import httpx
import re

Visited = []
urlActual = ""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
}

    
URL_REGEX =  r"^https?:\/\/[a-zA-Z0-9.-]+"

Search = { #stuff to find
    "api-key" : r'"[a-zA-Z0-9]{32,200}\s*"',   # Algolia and Typsense format api-key
    "URL" : r'^"platform-typesense-service-prod\..*\.io"', #Trying to find URL querys
    "Typesense" : r'SearchClient\([a-zA-Z0-9\(\)\[\]\{\}\.\'",:\-]*\)', # find Typesense Search
    "pre-Algolia": r'(\w*algolia\w*?):"(.+?)"', #find something named algonia
    "Algolia" : r'"(\w{10}|\w{32})"\s*,\s*"(\w{10}|\w{32})"' #find if they put directly in it
}

def searchRegex(html: str, regex):
    found = re.findall(Search[regex], html)
    found = [f"{regex}: {key}" for key in found]
    return found if found else None

def getPageData(url):
    try:
        response = httpx.get(url, headers=HEADERS)
        sel = Selector(response.text)
        scripts = sel.xpath("//script/@src").getall()
        scripts += sel.xpath("//link[@as='script']/@href").getall()
        pages = sel.xpath("//a/@href").getall()
        return response, scripts, pages
    except Exception as error:
        print(error)

def getNewUrls(pages):
    redirect = []
    for newUrl in pages:    
        tmp = re.findall(URL_REGEX, newUrl)
        tmp.append("")
        if tmp[0] != "" and not (tmp[0] in Visited) :
            redirect += tmp[0]
    return list(set(redirect))

def FoundAllRegex(script):
    results = []
    for regex in Search:
        if found := searchRegex(script, regex):
            results += found
    return results

def SearchRegexInScripts(scripts):
    results = []
    for script in scripts:
        print(f"looking for the regex in script: {script}")
        try:
            resp = httpx.get(urljoin(urlActual, script), headers=HEADERS)
        except Exception as error:
            print(error)
            continue
        if found:= FoundAllRegex(resp.text):
            results += found
    return results

def Crawler(url, maxProfundidad):
    global Visited
    global urlActual
    urlActual = url
    print(url)
    
    Visited.append(url)
    response, scripts, pages = getPageData(url)
    print(response)
    print(response.is_error)
    redirect = getNewUrls(pages)
    prioridades = ["app", "settings", "main"]
    
    scripts = sorted(scripts, key=lambda script: any(key in script for key in prioridades), reverse=True)
    print(f"found {len(scripts)} script files in {url}")
    results = SearchRegexInScripts(scripts)
    results += FoundAllRegex(response.text)
    if results:
        print(f"find {len(results)} in {url}")
        with open(f'Output/{url.removeprefix("https://")}.txt', 'w') as file:
            file.writelines(x + "\n" for x in results)
    else:
        print(f"could not find any in {len(scripts)} script details")
    
    if redirect and maxProfundidad > 0:
        Crawler((newUrl for newUrl in redirect), maxProfundidad-1)
    
## input
try:
    Crawler('https://alternativeto.net', 0)
except Exception as error:
    print(error)
    print("FINALIZADO POR ERROR")
finally:
    with open(f'Output/Visitados.txt', 'w') as file:
            file.writelines(x + "\n" for x in Visited)

