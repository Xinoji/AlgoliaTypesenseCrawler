from parsel import Selector
from urllib.parse import urljoin
import httpx
import re
import random

Visited = []
urlActual = ""
PROFUNDIDAD_MAXIMA = 10

HEADERS = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "en-US,en;q=0.8",
"Cache-Control": "max-age=0",
"Sec-Ch-Ua":'"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
"Sec-Ch-Ua-Mobile": "?0",
"Sec-Ch-Ua-Platform": '"Linux"',
"Sec-Fetch-Dest": "document",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Site": "same-origin",
"Sec-Fetch-User": "?1",
"Sec-Gpc": "1",
"Upgrade-Insecure-Requests":"1",
"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
}

START_URL = 'https://www.flat.mx/'

URL_REGEX =  [
    START_URL + r"\/.*" # websites from the start url
    #r"^https?:\/\/[a-zA-Z0-9.-]+\/.*" #any root domain website
    ]

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
        for regex in URL_REGEX:
            tmp = re.findall(regex, newUrl)
            tmp.append("")
            tmp[0] = urljoin(urlActual, tmp[0]) 
            if tmp[0] != "" and not (tmp[0] in Visited):
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
    results = SearchRegexInScripts([url] + scripts)
    results += FoundAllRegex(response.text)
    if results:
        results = list(set(results))
        print(f"find {len(results)} in {url}")
        with open(f'Output/{url.removeprefix("https://")}.txt', 'w') as file:
            file.writelines(x + "\n" for x in results)
    else:
        print(f"could not find any in {len(scripts)} script details")
    
    if redirect and maxProfundidad != 0:
        Crawler((newUrl for newUrl in redirect), maxProfundidad-1)
    
## input
try:
    Crawler(START_URL, PROFUNDIDAD_MAXIMA)
except Exception as error:
    print(error)
    print("FINALIZADO POR ERROR")
finally:
    with open(f'Output/Visitados.txt', 'w') as file:
            file.writelines(x + "\n" for x in Visited)

