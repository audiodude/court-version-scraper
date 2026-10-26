# Court Version Scraper

A web app that scrapes information from the PACER court listings and displays it.

This app is currently deployed on Fly.io: https://court-version-scraper.fly.dev/

It currently only grabs the court's ECF version, but could easily be extended to grab more information.

The data that is used to generate the web page can also be obtained in JSON format by running: `$ python scrape.py`.
Court pages are fetched in parallel, so a full scrape takes about 10 seconds. This JSON data is also available at the URL /courts.json (https://court-version-scraper.fly.dev/courts.json).

The production version of this application stores the scraped data in a hosted [memcached](http://memcached.org/)
instance (MemCachier) for 3 days. When the cache is empty, the next request re-scrapes and refills it.

The web server part of the project is written in the Python [Flask](https://flask.palletsprojects.com/) web framework.

### Installation and development

First:

```bash
pip -r requirements.txt
```

Then:

```bash
FLASK_DEBUG=true FLASK_APP=app.py flask run
```

If you have MEMCACHIER credentials, you can provide them to let your development server connect
to the production dataset:

    MEMCACHIER_PASSWORD=1234 MEMCACHIER_SERVERS=foobar.memcachier.com:11211 MEMCACHIER_USERNAME=1234 FLASK_DEBUG=true FLASK_APP=app.py flask run

### Deployment

First install the [Fly,io CLI app](https://fly.io/docs/flyctl/). Then:

```bash
fly deploy
```

### Legal

Author: Travis Briggs (briggs.travis@gmail.com)

Licensed under the MIT License, see LICENSE.md
