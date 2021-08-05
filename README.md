# OpenCitations-Bot
A bot to add citation data from OpenCitations to Wikidata
## Attribution
This is a bot created by Houcemeddine Turki, member of Data Engineering and Semantics Research Team in University of Sfax, Tunisia with the special contributions of Dennis Priskorn from Mid Sweden University, Sweden. This bot allows the enrichment of Wikidata items about scholarly publications with citation data from OpenCitations, an open bibliographic citation database in RDF format. The work is issued under CC BY-NC-SA 4.0 License. This license allows users to freely share and adapt this Python code in condition of the non-use of this effort in commercial purposes and the attribution of the work to its original authors.
## Principle
This bot uses the database of Wikidata items with DOI as retrieved by James Hare as of August 20, 2020 (https://figshare.com/articles/dataset/Wikidata_items_with_DOIs_2020-08-20/13063985). Then, it uses the REST API of OpenCitations to retrieve the DOI of the references and citing works of each publication. Finally, the obtained DOI are converted to Wikidata ID using the Wikidata Hub and the final output is automatically added to Wikidata using QuickStatements API. The source code of this bot is build using Python 3.5. Such a process does not cause any legal concern as Wikidata and OpenCitations scholarly knowledge graphs are both issued under CC0 License.
## Source Codes
* **OCtoWikidata**: Uses OpenCitations COCI REST API (https://opencitations.net/index/api/v1/) and Wikibase Integrator (https://github.com/LeMyst/WikibaseIntegrator) to: 
  * Find the DOIs of the references of scholarly papers indexed in the Wikidata Knowledge Graph.
  * Add missing *cites work* relations to Wikidata.
  * Identify the missing scholarly papers in Wikidata that are supported by OpenCitations.
  * Create Wikidata items for missing scholarly papers.
* When using the Python code, you will be required to change <USERNAME> by the username of your bot account and <PASSWORD> by the password of your bot account. Please ensure that you do not share your credentials when reusing the source code in your repository.
