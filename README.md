# OpenCitations-Bot
A bot to add citation data from OpenCitations to Wikidata

This is a bot created by Houcemeddine Turki, member of Data Engineering and Semantics Research Team in University of Sfax, Tunisia. This bot allows the enrichment of Wikidata items about scholarly publications with citation data from OpenCitations, an open bibliographic citation database in RDF format.
## Principle
This bot retrieves the Wikidata ID and DOI of scholarly publications using Wikidata Query Service. Then, it uses the REST API of OpenCitations to retrieve the DOI of the references and citing works of each publication. Finally, the obtained DOI are converted to Wikidata ID using the WDumper-based dump and the final output is automatically added to Wikidata using QuickStatements API. The source code of this bot is build using Python 3.5. Such a process does not cause any legal concern as Wikidata and OpenCitations scholarly knowledge graphs are both issued under CC0 License.
