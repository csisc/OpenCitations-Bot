# OpenCitations Bot
# Created By Houcemeddine Turki

import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import requests
import csv

#Retrieving scientists from Wikidata
endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT * WHERE {
  ?x wdt:P31 wd:Q5.
  {?x wdt:P106 wd:Q1650915.} UNION {?x wdt:P106 wd:Q901.}
  }"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

try:
    results = get_results(endpoint_url, query)
except:
    print("Matter1")

#Retrieving the publications of each scientist
with open('batch.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for result in results["results"]["bindings"]:
        sc = result["x"]["value"][31:255]
        query1 = """SELECT * WHERE {
         ?x wdt:P31 wd:Q13442814.
         ?x wdt:P50 wd:"""+sc+""".
         ?x wdt:P356 ?doi.
        }"""
        try:
            results1 = get_results(endpoint_url, query1)
        except:
            print("Matter2")
        for result1 in results1["results"]["bindings"]:
            p = result1["x"]["value"][31:255]
            doi = result1["doi"]["value"]
            ss = "https://w3id.org/oc/index/api/v1/metadata/"+doi
            try:
                rp = requests.get(ss)
            except:
                print("Matter3")
            #Extracting the metadata of each publication
            da = rp.json()
            for result2 in da:
                our='"'+result2["oa_link"]+'"'
                spamwriter.writerow([p, "P2699", our,"S248","Q29279836"])
                cit = result2["citation"].split("; ")
                for c1 in cit:
                    query21 = '''SELECT * WHERE {
                      ?p wdt:P31 wd:Q13442814.
                      ?p wdt:P356 "'''+c1+'''".
                    }'''
                    try:
                        cond = False
                        results21 = get_results(endpoint_url, query21)
                        for result21 in results21["results"]["bindings"]:
                            spamwriter.writerow([result21["p"]["value"][31:255],"P2860",p,"S248","Q29279836"])
                            cond = True
                        if (cond == False):
                            spamwriter.writerow(["CREATE"])
                            spamwriter.writerow(["LAST","P2860",p,"S248","Q29279836"])
                            sv = "https://w3id.org/oc/index/api/v1/metadata/"+c1
                            try:
                                rv = requests.get(sv)
                                dv = rv.json()
                                for result3 in dv:
                                    titc = '"'+result3["title"]+'"'
                                    spamwriter.writerow(["LAST","Len",titc])
                                    spamwriter.writerow(["LAST","Den","Scholarly article"])
                                    spamwriter.writerow(["LAST","P1476",titc,"S248","Q29279836"])
                                    issc = '"' + result3["issue"] + '"'
                                    spamwriter.writerow(["LAST","P433",issc,"S248","Q29279836"])
                                    volc = '"' + result3["volume"] + '"'
                                    spamwriter.writerow(["LAST","P478",volc,"S248","Q29279836"])
                                    autc = result3["author"].split("; ")
                                    for auth in autc:
                                        autn = auth.split(", ")
                                        autf = '"' + autn[1] + " " + autn[0] + '"'
                                        spamwriter.writerow(["LAST","P2093",autf,"S248","Q29279836"])
                                    yeac = '"' + result3["year"] + '"'
                                    spamwriter.writerow(["LAST","P577",yeac,"S248","Q29279836"])
                                    pagc = '"' + result3["page"] + '"'
                                    spamwriter.writerow(["LAST","P304",pagc,"S248","Q29279836"])
                                    doic = '"' + result3["doi"] + '"'
                                    spamwriter.writerow(["LAST","P356",doic,"S248","Q29279836"])
                                    urlc = '"' + result3["oa_link"] + '"'
                                    spamwriter.writerow(["LAST","P2699",urlc,"S248","Q29279836"])
                                    srcc = '"' + result3["source_title"] + '"'
                                    query4 = query = """SELECT ?x ?label WHERE {
                                      { ?x wdt:P31 wd:Q737498. }
                                      UNION
                                      { ?x wdt:P31 wd:Q5633421. }
                                      UNION
                                      { ?x wdt:P31 wd:Q2020153. }
                                      UNION
                                      {
                                        ?x wdt:P31 ?y.
                                        ?y wdt:P279 wd:Q1235234.
                                      }
                                      UNION
                                      { ?x wdt:P31 wd:Q1143604. }
                                      ?x rdfs:label ?label.
                                      FILTER((LANG(?label)) = "en")
                                      FILTER(STRSTARTS(?label, """+srcc+"""))
                                    }"""
                                    try:
                                        results4 = get_results(endpoint_url, query4)
                                        sn = 1
                                        for rr in results4:
                                            if (result3["source_title"]== rr["label"]["value"]): spamwriter.writerow(["LAST","P50",rr["x"]["value"][31:255],"P1545",s,"S248","Q29279836"])
                                            sn += 1
                                    except:
                                        print("Matter4")
                            except:
                                print("Matter5")     
                    except:
                        print("Matter6")
                    
                ref = result2["reference"].split("; ")
                for r1 in ref:
                    query21 = '''SELECT * WHERE {
                      ?p wdt:P31 wd:Q13442814.
                      ?p wdt:P356 "'''+r1+'''".
                    }'''
                    try:
                        cond = False
                        results21 = get_results(endpoint_url, query21)
                        for result21 in results21["results"]["bindings"]:
                            spamwriter.writerow([p,"P2860",result21["p"]["value"][31:255],"S248","Q29279836"])
                            cond = True
                        if (cond == False):
                            spamwriter.writerow(["CREATE"])
                            sv = "https://w3id.org/oc/index/api/v1/metadata/"+r1
                            try:
                                rv = requests.get(sv)
                                dv = rv.json()
                                for result3 in dv:
                                    titc = '"'+result3["title"]+'"'
                                    spamwriter.writerow(["LAST","Len",titc])
                                    spamwriter.writerow(["LAST","Den","Scholarly article"])
                                    spamwriter.writerow(["LAST","P1476",titc,"S248","Q29279836"])
                                    issc = '"' + result3["issue"] + '"'
                                    spamwriter.writerow(["LAST","P433",issc,"S248","Q29279836"])
                                    volc = '"' + result3["volume"] + '"'
                                    spamwriter.writerow(["LAST","P478",volc,"S248","Q29279836"])
                                    autc = result3["author"].split("; ")
                                    for auth in autc:
                                        autn = auth.split(", ")
                                        autf = '"' + autn[1] + " " + autn[0] + '"'
                                        spamwriter.writerow(["LAST","P2093",autf,"S248","Q29279836"])
                                    yeac = '"' + result3["year"] + '"'
                                    spamwriter.writerow(["LAST","P577",yeac,"S248","Q29279836"])
                                    pagc = '"' + result3["page"] + '"'
                                    spamwriter.writerow(["LAST","P304",pagc,"S248","Q29279836"])
                                    doic = '"' + result3["doi"] + '"'
                                    spamwriter.writerow(["LAST","P356",doic,"S248","Q29279836"])
                                    urlc = '"' + result3["oa_link"] + '"'
                                    spamwriter.writerow(["LAST","P2699",urlc,"S248","Q29279836"])
                                    srcc = '"' + result3["source_title"] + '"'
                                    query4 = query = """SELECT ?x ?label WHERE {
                                      { ?x wdt:P31 wd:Q737498. }
                                      UNION
                                      { ?x wdt:P31 wd:Q5633421. }
                                      UNION
                                      { ?x wdt:P31 wd:Q2020153. }
                                      UNION
                                      {
                                        ?x wdt:P31 ?y.
                                        ?y wdt:P279 wd:Q1235234.
                                      }
                                      UNION
                                      { ?x wdt:P31 wd:Q1143604. }
                                      ?x rdfs:label ?label.
                                      FILTER((LANG(?label)) = "en")
                                      FILTER(STRSTARTS(?label, """+srcc+"""))
                                    }"""
                                    try:
                                        results4 = get_results(endpoint_url, query4)
                                        sn = 1
                                        for rr in results4:
                                            if (result3["source_title"]== rr["label"]["value"]): spamwriter.writerow(["LAST","P50",rr["x"]["value"][31:255],"P1545",sn,"S248","Q29279836"])
                                            sn += 1
                                    except:
                                        print("Matter7")
                            except:
                                print("Matter8")     
                    except:
                        print("Matter9")                    
                csvfile.flush()
