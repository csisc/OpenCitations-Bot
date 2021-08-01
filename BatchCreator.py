import requests

with open("output.tsv", "r") as f:
  with open("batch.tsv", "w", encoding="utf-8") as f1:
    for x in f:
      if (x.find("MISSING")>=0):
          f1.write("CREATE\n")
          f1.write("LAST\tP31\tQ13442814\tS248\tQ107507940\n")
          doi = x[8:-1]
          f1.write('LAST\tP356\t"'+doi+'"\tS248\tQ107507940\n')
          r = requests.get("https://opencitations.net/index/api/v1/metadata/"+doi)
          r_json = r.json()
          for rec in r_json:
              try:
                  n = 0
                  author = rec["author"]
                  aut = author.split("; ")
                  for a in aut:
                      n += 1
                      if (a.find(", ")>=0):
                          aus = a.split(", ")
                          f1.write('LAST\tP2093\t"'+aus[1]+' '+aus[0]+'"\tP1545\t"'+str(n)+'"\tS248\tQ107507940\n')
                      else:
                          f1.write('LAST\tP2093\t"'+a+'"\tP1545\t"'+str(n)+'"\tS248\tQ107507940\n')                  
              except KeyError:
                  author = ""
              try:
                  year = str(rec["year"])
                  if (year != ""): f1.write('LAST\tP577\t+'+year+'-00-00T00:00:00Z/9\tS248\tQ107507940\n')
              except KeyError:
                  year = ""
              try:
                  title = str(rec["title"])
                  f1.write('LAST\tLen\t"'+title+'"\n')
                  f1.write('LAST\tP1476\ten:"'+title+'"\tS248\tQ107507940\n')
              except KeyError:
                  title = ""
              try:
                  sourcetitle = str(rec["source_title"])
                  if (sourcetitle != ""): f1.write('LAST\tP1433\tQ53569537\tP1932\t"'+sourcetitle+'"\tS248\tQ107507940\n')
              except KeyError:
                  sourcetitle = ""
                  
              try:
                  volume = str(rec["volume"])
                  if (volume != ""): f1.write('LAST\tP478\t"'+volume+'"\tS248\tQ107507940\n')
              except KeyError:
                  volume = ""
              try:
                  issue = str(rec["issue"])
                  if (issue != ""): f1.write('LAST\tP433\t"'+issue+'"\tS248\tQ107507940\n')
              except KeyError:
                  issue = ""
              try:
                  page = str(rec["page"])
                  if (page != ""): f1.write('LAST\tP304\t"'+page+'"\tS248\tQ107507940\n')
              except KeyError:
                  page = ""
              try:
                  oalink = str(rec["oa_link"])
                  if (oalink != ""): f1.write('LAST\tP856\t"'+oalink+'"\tS248\tQ107507940\n')
              except KeyError:
                  oalink = ""
      else:
          f1.write(x)
