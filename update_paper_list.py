from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
date_time = datetime.now()
str_date_time = date_time.strftime("%Y%m%d")

# Here you provide your credentials
# or run in a live environment a la iPython
#username = "XXX" # for OpenReview scraping
#pwd = "YYY"


# strings to search for
keywords = ["causal", "interv", "counterf"]


"""
Here follow all different scrapers.
"""
def scrape_neurips_proceeding(proceedings_url, conf=None):
    """
    Regular NeurIPS Proceedings Site
    """
    page = urlopen(proceedings_url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    papers = soup.find_all("li")[2:]
    d = {}
    for k in keywords:
        papers_filtered = [(ind, p) for (ind, p) in enumerate(papers) if k in str(p).lower()]
        print(f"Searching {proceedings_url}, Found {len(papers_filtered)} papers with keyword {k}")
        for (ind, p) in papers_filtered:
            title = p.find("a").contents[0]
            authors = ", ".join(p.find("i").contents)
            url = "https://papers.nips.cc/" + p.find("a").attrs["href"]
            d.update({ind: {"title": title, "authors": authors, "url": url, "conference": conf}})
    return d

def scrape_neurips_announcement(proceedings_url, conf=None):
    """
    NeurIPS announcement of accepted papers before regular proceedings
    """
    page = urlopen(proceedings_url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    papers = soup.find_all("div", {"class": "maincardBody"})
    all_authors = soup.find_all("div", {"class": "maincardFooter"})
    d = {}
    for k in keywords:
        papers_filtered = [(ind,p) for (ind,p) in enumerate(papers) if k in str(p).lower()]
        print(f"Searching {proceedings_url}, Found {len(papers_filtered)} papers with keyword {k}")
        for (ind,p) in papers_filtered:
            title = p.contents[0]
            authors = ", ".join("".join(all_authors[ind].contents).split(" · "))
            url = "-"
            d.update({ind: {"title": title, "authors": authors, "url": url, "conference": conf}})
    return d

def scrape_mlr_proceedings(proceedings_url, conf=None):
    """
    This is for ICML and AIStats
    """
    page = urlopen(proceedings_url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    papers = soup.find_all("div", {"class": "paper"})
    d = {}
    for k in keywords:
        papers_filtered = [(ind,p) for (ind,p) in enumerate(papers) if k in str(p).lower()]
        print(f"Searching {proceedings_url}, Found {len(papers_filtered)} papers with keyword {k}")
        for (ind,p) in papers_filtered:
            title = p.find("p", {"class":"title"}).contents[0]
            authors = p.find("span", {"class":"authors"}).text.replace(u"\xa0",u" ")
            url = p.find("p", {"class": "links"}).contents[1].attrs["href"]
            d.update({ind: {"title": title, "authors": authors, "url": url, "conference": conf}})
    return d

def scrape_clear_papers(proceedings_url, conf=None, year=2022, api=""):
    """
    One needs an OpenReview account to use the API as regular scraping is not possible
    """
    import openreview
    #year = int(proceedings_url.split("/")[-3]) # make sure you get the year
    if year < 2022:
        return Exception("Capture year first.")
    if username is None or pwd is None:
        return Exception("Provide your OpenReview Credentials first.")
    client = openreview.Client(baseurl=f'https://api{api}.openreview.net',
                               username=username,
                               password=pwd)
    # venues = client.get_group(id='venues').members
    papers = client.get_all_notes(invitation=f'cclear.cc/CLeaR/{year}/Conference/-/Blind_Submission')
    d = {}
    #for k in keywords:
    #    papers_filtered = papers # CLeaR is an all out causal conference, so no filtering #[(ind,p) for (ind,p) in enumerate(papers) if k in str(p).lower()]
    print(f"Searching {proceedings_url}, Found {len(papers)} papers")
    for (ind,p) in enumerate(papers):
        title = p.content["title"]
        authors = ", ".join(p.content["authors"])
        if "anonymous" in authors.lower():
            continue
        url = "https://openreview.net" + p.content["pdf"]
        d.update({ind: {"title": title, "authors": authors, "url": url, "conference": conf}})
    return d

def scrape_neurips_iclr_openreview(proceedings_url, conf=None, year=2022, api=1):
    """
    One needs an OpenReview account to use the API as regular scraping is not possible
    This function is a bit different than the others, as it will capture papers that contain the keywords
    within any of the Meta-Data including Abstract, TL;DR, Tags (so not just title)
    conf = NeurIPS or ICLR
    """
    import openreview
    #year = int(proceedings_url.split("/")[-3]) # make sure you get the year
    if year < 2022:
        return Exception("Capture year first.")
    if username is None or pwd is None:
        return Exception("Provide your OpenReview Credentials first.")
    client = openreview.Client(baseurl=f'https://api{api}.openreview.net',
                               username=username,
                               password=pwd)
    # venues = client.get_group(id='venues').members
    venueid = f'{conf}.cc/{year}/Conference'
    papers = client.get_all_notes(content={'venueid':f'{conf}.cc/{year}/Conference'})
    d = {}
    for k in keywords:
        papers_filtered = [(ind,p) for (ind,p) in enumerate(papers) if k in str(p).lower()]
        print(f"Searching {proceedings_url}, Found {len(papers_filtered)} papers with keyword {k} (somewhere in meta data, not just in title)")
        for (ind,p) in papers_filtered:
            if isinstance(p.content['title'], dict):
                title = p.content['title']["value"]
            else:
                title = p.content["title"]
            if isinstance(p.content['authors'], dict):
                authors_suffix = p.content['authors']["value"]
            else:
                authors_suffix = p.content['authors']
            authors = ", ".join(authors_suffix)
            if "anonymous" in authors.lower():
                continue
            if isinstance(p.content['pdf'],dict):
                url_suffix = p.content["pdf"]["value"]
            else:
                url_suffix = p.content["pdf"]
            url = "https://openreview.net" + url_suffix
            d.update({ind: {"title": title, "authors": authors, "url": url, "conference": conf}})
    return d



"""
The following list contains all the proceedings to be scraped.
"""
proceedings = [
    # (scrape_neurips_proceeding, "https://papers.nips.cc/paper/2021", "NeurIPS 2021"), # NeurIPS 2021
    # (scrape_neurips_openreview, "https://openreview.net/group?id=NeurIPS.cc/2022/Conference/", "NeurIPS 2022"), # (scrape_neurips_announcement,"https://nips.cc/Conferences/2022/Schedule?type=Poster", "NeurIPS 2022"),
    #
    # (scrape_mlr_proceedings, "https://proceedings.mlr.press/v139/", "ICML 2021"), # ICML 2021
    # (scrape_mlr_proceedings, "https://proceedings.mlr.press/v162/", "ICML 2022"),
    #
    # (None, "https://aaai.org/Conferences/AAAI-21/wp-content/uploads/2020/12/AAAI-21_Accepted-Paper-List.Main_.Technical.Track_.pdf", "AAAI 2021"), # note how AAAI uses PDF # AAAI 2021
    # (None, "https://aaai.org/Conferences/AAAI-22/wp-content/uploads/2021/12/AAAI-22_Accepted_Paper_List_Main_Technical_Track.pdf", "AAAI 2022"),
    #
    # (None, "https://www.auai.org/uai2021/accepted_papers", "UAI 2021"), # UAI 2021
    # (None, "https://www.auai.org/uai2022/accepted_papers", "UAI 2022"),
    #
    # (scrape_mlr_proceedings, "https://proceedings.mlr.press/v130/", "AIStats 2021"), # AIStats 2021
    # (scrape_mlr_proceedings, "https://proceedings.mlr.press/v151/", "AIStats 2022"),

    (scrape_clear_papers, "https://openreview.net/group?id=cclear.cc/CLeaR/2023/Conference/", "CLeaR", 2023, _), # CLeaR 2022
    (scrape_neurips_iclr_openreview, "https://openreview.net/group?id=NeurIPS.cc/2023/Conference/", "NeurIPS", 2023, 2), # requires API version 2
    (scrape_neurips_iclr_openreview, "https://openreview.net/group?id=ICLR.cc/2023/Conference/", "ICLR", 2023, _),

]

# location where paper list is being saved
save_path = f"Paper-List-{str_date_time}.csv"

# scrape procedure for all proceedings
results = []
sum_papers = 0
for (f,p,c,y,a) in proceedings:
    if f is None:
        print(f"Skipping {p} since scraper not implemented")
        continue
    papers = f(p,c,y,a)
    sum_papers += len(papers)
    results.append(papers)
print(f"**** Scraping Complete: A total of {sum_papers} papers found across {len(proceedings)} proceedings.")

# actual saving of scraped
df = pd.concat([pd.DataFrame.from_dict(r).T for r in results])
df.to_csv(save_path, index=False)
print(f"Saved to CSV: {save_path}")
