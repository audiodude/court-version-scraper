import flask

import scrape

app = flask.Flask(__name__)

@app.route('/')
def index():
  all_courts = scrape.get_all_courts()
  return flask.render_template('index.html', all_courts=all_courts)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
