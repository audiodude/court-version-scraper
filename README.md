Court Version Scraper
=====================
A web app that scrapes information from the PACER court listings and displays it.

This app is currently deployed on Heroku: http://court-version-scraper.herokuapp.com/

It currently only grabs the court's ECF version, but could easily be extended to grab more information.

The data that is used to generate the web page can also be obtained in JSON format by running: `$ python scrape.py`.
It takes about 3-4 minutes to download all of the relevant court pages. This JSON data is also available at the URL /courts.json (so for the Heroku deploy, http://court-version-scraper.herokuapp.com/courts.json)

Because it takes so long to download the pages, the production version of this application uses a hosted
[memcached](http://memcached.org/) instance to store the scraped data. This data is cached indefinitely. There is a
Heroku scheduled job (`$ python scrape.py -f`) which runs daily to refresh the contents of the cache.

The web server part of the project is written in the Python [Flask](http://flask.pocoo.org/) web framework.

### Legal
Author: Travis Briggs (briggs.travis@gmail.com)

Licensed under the MIT License, see LICENSE.md
