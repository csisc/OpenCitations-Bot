import requests

f = open("wikidata_doi.tsv", "r")
with open("output.tsv", "w") as f1:
    for x in f:
      t = x.split("\t")
      wid = t[0]
      doi = t[1][1:-2]
      r = requests.get('https://opencitations.net/index/api/v1/references/'+doi)
      r_data = r.text
      s = []
      while (r_data.find('"cited": "coci => ') >= 0):
          r_data = r_data[r_data.find('"cited": "coci => ')+18:]
          s.append(r_data[0:r_data.find('"')])
      s1 = []
      for i in s:
          idurl = "https://hub.toolforge.org/P356:"+i+"?format=json"
          idget = requests.get(idurl)
          idjson = idget.json()
          try:
              wid1 = idjson["origin"]["qid"]
          except KeyError:
              wid1 = ""
          if (wid1 != ""):
              f1.write(wid+"\tP2860\t"+wid1+"\tS248\tQ107507940\n")
              f1.flush()
          else:
              f1.write("MISSING\t"+i+"\n")
              f1.flush()
      print(s1)
  
