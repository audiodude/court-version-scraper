Court Version Scraper
=====================
A web app that scrapes information from the PACER court listings and displays it.

This app is currently deployed on Heroku: http://pacer-court-scraper.herokuapp.com/

It currently only grabs the court's ECF version, but could easily be extended to grab more information.

The data that is used to generate the web page can also be obtained in JSON format by running: `$ python scrape.py`.
It takes about 3-4 minutes to download all of the relevant court pages.

Because it takes so long to download the pages, the production version of this application uses a hosted
[memcached](http://memcached.org/) instance to store the scraped data. This data is cached indefinitely. There is a
Heroku scheduled job (`$ python scrape.py -f`) which runs daily to refresh the contents of the cache.

The web server part of the project is written in [Flask](http://flask.pocoo.org/).

### Installation

First, you need `memcached` and its dev libs. 

On Ubuntu, you can do:

    sudo apt-get install libmemcached-dev

Then:

    pip -r requirements.txt

### Legal
Author: Travis Briggs (briggs.travis@gmail.com)

Licensed under the MIT License, see LICENSE.md
