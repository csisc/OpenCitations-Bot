import datetime
import os

import requests
from wikibaseintegrator import wbi_core, wbi_login, wbi_datatype
from wikibaseintegrator.wbi_config import config as wbi_config

# Pseudo code
# (first download the 280 MB data from James Hare linked in the README) 
# log in to Wikidata
# get current date
# prepare reference to be used later on statements
# open the data-file
# for each line:
## parse the line and extract wikidata_item_id and DOI
## lookup the DOI in COCI
## parse the COCI data
## for each reference in the COCI data:
### check via hub if DOI is already in Wikidata
### if found:
#### add reference as "cited work"
### else:
##### create new item from the COCI data
##### add author statement
##### add publication year statement
##### add research venu aka published in statement
##### add source title statement
##### add volume statement
##### add issue statement
##### add page numbers statement
##### add open access link statement
##### add set description statement
## upload to Wikidata

# Check if dependencies exist
if not os.path.isfile('wikidata_doi.tsv'):
    print('ERROR: You need to manually download the file wikidata_doi.tsv. Instructions in README.md.')
    exit(-1)

# Setting Custom User Agent
__version__ = 'dev'
wbi_config['USER_AGENT_DEFAULT'] = "OpenCitations-Bot/{} (https://github.com/csisc/OpenCitations-Bot)".format(__version__)

# Get environment variables
USER = os.getenv('WIKIDATA_USER')
PASSWORD = os.environ.get('WIKIDATA_PASSWORD')
DEBUG = os.environ.get('DEBUG', False) == '1'
STARTING_LINE = int(os.environ.get('STARTING_LINE', 0))

# Logging in with Wikibase Integrator
print("Logging in with Wikibase Integrator")
login_instance = wbi_login.Login(user=USER, pwd=PASSWORD)

# Getting the current date
datestr = '+' + str(datetime.datetime.now())[0:10] + 'T00:00:00Z'

# Opening the list of Wikidata items with DOI
file = open("wikidata_doi.tsv", "r")

# Setting COCI as a reference for the created statements
cit_wikidata_id = ""
source = [
    [
        wbi_datatype.ItemID(value="Q107507940", prop_nr="P248", is_reference=True, if_exists="APPEND"),
        wbi_datatype.Time(time=datestr, prop_nr="P813", is_reference=True, if_exists="APPEND"),
        wbi_datatype.Url(value="https://opencitations.net/index/coci/api/v1", prop_nr="P854", is_reference=True, if_exists="APPEND")
    ]
]

for i, line in enumerate(file):
    # Skipping lines
    if i < STARTING_LINE:
        continue

    # Extracting the Wikidata ID and DOI of every single publication from the list of Wikidata items with DOI
    line_elements = line.split("\t")
    wid = line_elements[0]
    doi = line_elements[1][1:-2]

    if DEBUG:
        print('Doing {}'.format(doi))

    # Getting the references for every scholarly article
    r = requests.get('https://opencitations.net/index/api/v1/references/' + doi)
    r_data = r.text
    ref_dois = []

    # Extracting the DOIs of the references for every scholarly article
    while r_data.find('"cited": "coci => ') >= 0:
        r_data = r_data[r_data.find('"cited": "coci => ') + 18:]
        ref_dois.append(r_data[0:r_data.find('"')])

    # Retrieving Wikidata ID for every DOI
    statements = []
    for refdoi in ref_dois:
        idurl = "https://hub.toolforge.org/P356:" + refdoi + "?format=json"
        idget = requests.get(idurl)
        idjson = idget.json()
        if 'origin' in idjson and 'qid' in idjson['origin']:
            cit_wikidata_id = idjson["origin"]["qid"]
        else:
            cit_wikidata_id = ""
        # Identifying the missing cites work relations in Wikidata
        if cit_wikidata_id != "":
            statement = wbi_datatype.ItemID(value=cit_wikidata_id, prop_nr="P2860", references=source, if_exists="APPEND")
            statements.append(statement)
        else:
            # Prepare statements for a new item
            new_item_statements = []

            # Getting the metadata of the reference publication to be added to Wikidata
            response = requests.get("https://opencitations.net/index/api/v1/metadata/" + refdoi)

            # Adding DOI Statements for new items
            doi_statement = wbi_datatype.ExternalID(value=refdoi, prop_nr="P356", references=source)
            new_item_statements.append(doi_statement)
            opencitations_json = response.json()

            title = ''
            year = ''
            sourcetitle = ''

            for record in opencitations_json:
                if 'author' in record:
                    n = 0
                    # Adding Authorship Statements for new items
                    author = record["author"]
                    authorlist = author.split("; ")
                    for a in authorlist:
                        n += 1
                        strn = str(n)
                        if a.find(", ") >= 0:
                            aus = a.split(", ")
                            str1 = aus[1] + ' ' + aus[0]
                            authorqualifier = [
                                wbi_datatype.String(value=strn, prop_nr="P1545", is_qualifier=True)
                            ]
                            author = wbi_datatype.String(value=str1, prop_nr="P2093", qualifiers=authorqualifier, references=source)
                            new_item_statements.append(author)
                        else:
                            authorqualifier = [
                                wbi_datatype.String(value=strn, prop_nr="P1545", is_qualifier=True)
                            ]
                            author = wbi_datatype.String(value=a, prop_nr="P2093", qualifiers=authorqualifier, references=source)
                            new_item_statements.append(author)
                else:
                    author = ""
                # Adding Publication Years for new items
                if 'year' in record:
                    year = str(record["year"])
                    if year != "":
                        year1 = wbi_datatype.Time(time='+' + year + '-00-00T00:00:00Z', prop_nr="P577", precision=9, references=source)
                        new_item_statements.append(year1)
                else:
                    year = ""

                # Extracting the titles for new items
                if 'title' in record:
                    title = str(record["title"])
                else:
                    title = ''

                # Reconciling the research venue to corresponding Wikidata items
                if 'source_id' in record:
                    sourceid = str(record["source_id"])
                else:
                    sourceid = ""

                if sourceid.find("issn") >= 0:
                    venueid = sourceid[5:14]
                    venuewikidatareconcilel = "https://hub.toolforge.org/P236:" + venueid + "?format=json"
                    venueget = requests.get(venuewikidatareconcilel)
                    venuejson = venueget.json()
                    if 'origin' in venuejson and 'qid' in venuejson['origin']:
                        sourcewikidataid = venuejson["origin"]["qid"]
                        sourcewid1 = wbi_datatype.ItemID(value=sourcewikidataid, prop_nr="P1433", references=source)
                        new_item_statements.append(sourcewid1)
                    else:
                        sourcewikidataid = ""

                    # Adding Source Titles to new items
                    if sourcewikidataid == "":
                        if 'source_title' in record:
                            sourcetitle = str(record["source_title"])
                            if sourcetitle != "":
                                sourcequalifier = [
                                    wbi_datatype.String(value=sourcetitle, prop_nr="P1932", is_qualifier=True)
                                ]
                                source1 = wbi_datatype.ItemID(value="Q53569537", prop_nr="P1433", qualifiers=sourcequalifier, references=source)
                                new_item_statements.append(source1)
                        else:
                            sourcetitle = ""

                # Adding Volume Number to new items
                if 'volume' in record:
                    volume = str(record["volume"])
                    if volume != "":
                        volume1 = wbi_datatype.String(value=volume, prop_nr="P478", references=source)
                        new_item_statements.append(volume1)
                else:
                    volume = ""

                # Adding Issue Number to new items
                if 'issue' in record:
                    issue = str(record["issue"])
                    if issue != "":
                        issue1 = wbi_datatype.String(value=issue, prop_nr="P433", references=source)
                        new_item_statements.append(issue1)
                else:
                    issue = ""

                # Adding Page Numbers to new items
                if 'page' in record:
                    page = str(record["page"])
                    if page != "":
                        page1 = wbi_datatype.String(value=page, prop_nr="P304", references=source)
                        new_item_statements.append(page1)
                else:
                    page = ""

                # Adding Open Access Link Statements to new items
                if 'oa_link' in record:
                    oalink = str(record["oa_link"])
                    if oalink != "":
                        oa = wbi_datatype.Url(value=oalink, prop_nr="P856", references=source)
                        new_item_statements.append(oa)
                else:
                    oalink = ""

            # Preparing the batch to create a new item
            item = wbi_core.ItemEngine(data=new_item_statements, debug=DEBUG)

            # Setting a description for the new Wikidata item
            if title != "":
                item.set_label(title, lang="en")
            if year != "":
                desc = "scholarly article published in " + year
            elif sourcetitle != "":
                desc = "scholarly article published in " + sourcetitle
            else:
                desc = "scholarly article"
            item.set_description(desc, lang="en")

            # Creating the new item
            if len(new_item_statements) >= 2:
                try:
                    item.write(login_instance, edit_summary="Uploaded from OpenCitations COCI API using [[User:OpenCitations Bot|OpenCitations Bot]]")
                except Exception:
                    print("New item not created.")
                    if DEBUG:
                        raise
    if statements:
        # Adding Cites Work Relations to Wikidata
        item = wbi_core.ItemEngine(data=statements, item_id=wid)
        item.write(login_instance, edit_summary="Added from OpenCitations COCI API using [[User:OpenCitations Bot|OpenCitations Bot]]")
