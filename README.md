# ESS-Python
Python Scripts for Scraping Epigraphic Data
***
Goal is simple.

Unite the scripts used for scraping epigraphic data online under one banner.

Here are some guidelines:

* Crawlers should concern only open access sources

* Crawlers should respect to the rate limits imposed by the terms of use of the site

* Every site should have its own folder of its relative scrapers under the directory of the project.

* Tests for every function concerning the transformation of the scraped data are obligatory.

* If you want to include an examplary html page along with your test functions, which is recommended, the you must join the last access date to the name of page with an underscore, and mention it in docstrings of your main and test functions. Ex. somePage_20170212.html

* The output of the scrapers must either be a json file or a csv

* This is not a hub for scraping anything, it is only here for data related to ancient cultures.

____

**IMPORTANT!**

If the data provider thinks that a scraper invalidates their terms of use:

+ Contact to the organisation or the repository by manifesting in any way (create issue, etc.)
   
+ Explain why the scraper invalidates the terms of use.
   
+ At this point, we shall discuss if we can change the scraper so that it doesn't infringe the terms of use.
   
+ If no agreement is reached we shall exclude the scraper from our stable/master branch with a new commit.






