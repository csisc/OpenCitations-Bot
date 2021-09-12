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
    if statements:
        # Adding Cites Work Relations to Wikidata
        item = wbi_core.ItemEngine(data=statements, item_id=wid)
        item.write(login_instance, edit_summary="Added from OpenCitations COCI API using [[User:OpenCitations Bot|OpenCitations Bot]]")
