from parsel import Selector
from urllib.parse import urljoin
import httpx
import re
import random

countVisitados = 0
Visited = []
urlActual = ""
PROFUNDIDAD_MAXIMA = 10

# Generation of random Headers to evit been detected as scrapper by the site
def generate_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    ]

    platforms = ["Windows", "Linux", "Mac"]

    retHeaders = {
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.8",
        "Sec-Ch-Ua": f"\"{random.choice(user_agents)}\"",
        "Sec-Ch-Ua-Mobile": f"?{random.randint(0, 1)}",
        "Sec-Ch-Ua-Platform": f"\"{random.choice(platforms)}\"",
        "User-Agent": random.choice(user_agents),
    }

    return retHeaders

HEADERS = generate_random_headers()


START_URL = 'https://alternativeto.net/'

URL_REGEX =  [
    #START_URL + r"\/.*" # websites from the start url   
    r"^https?:\/\/[a-zA-Z0-9.-]+\/.*" #any root domain website
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
        return None, None, None

def getNewUrls(pages):
    redirect = []
    for newUrl in pages:
        newUrl = urljoin(urlActual, newUrl)
        for regex in URL_REGEX:
            tmp = re.findall(regex, newUrl)
            tmp.append("")
            if tmp[0] != "" and not (tmp[0] in Visited):
                redirect += [tmp[0]] 
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
    global Visited, urlActual, countVisitados
    urlActual = url
    print(url)
    
    Visited.append(url)
    response, scripts, pages = getPageData(url)
    redirect = getNewUrls(pages)
    prioridades = ["app", "settings", "main"]
    
    scripts = sorted(scripts, key=lambda script: any(key in script for key in prioridades), reverse=True)
    print(f"found {len(scripts)} script files in {url}")
    results = SearchRegexInScripts([url] + scripts)
    results += FoundAllRegex(response.text)
    if results:
        results = list(set(results))
        print(f"find {len(results)} in {url}")
        countVisitados += 1
        with open(f'Output/{countVisitados}.txt', 'w') as file:
            file.writelines(x + "\n" for x in results)
    else:
        print(f"could not find any in {len(scripts)} script details")
    
    if redirect and maxProfundidad != 0:
        for newUrl in redirect:
            Crawler(newUrl, maxProfundidad-1)
    
## input

try:
    Crawler(START_URL, PROFUNDIDAD_MAXIMA)
except Exception as error:
    print(error)
    print("FINALIZADO POR ERROR")
finally:
    with open(f'Output/Visitados.txt', 'w') as file:
            file.writelines(x + "\n" for x in Visited)