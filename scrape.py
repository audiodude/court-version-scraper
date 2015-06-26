from lxml import html, etree
import requests

def get_courts(root, marker_name):
  marker_anchors = root.xpath('//a[@name="%s"]' % marker_name)
  for marker in marker_anchors:
    court = None
    for sibling in marker.itersiblings():
      if (court and sibling.tag == 'a' and
          'courtinfo' in sibling.get('href')):
        yield {'court': court, 'info_link': sibling.get('href')}
        court = None
      elif not court and sibling.tag == 'a':
        court = sibling.text

def get_all_courts():
  COURT_MARKERS = ('APCTS', 'DCCTS', 'BKCTS')

  resp = requests.get('https://www.pacer.gov/psco/cgi-bin/links.pl')
  root = html.fromstring(resp.text)

  courts = []
  for marker in COURT_MARKERS:
    for info in get_courts(root, marker):
      info_resp = requests.get(info['info_link'])
      info_root = html.fromstring(info_resp.text)
      software_td = info_root.xpath(
        '//td[contains(text(), "Software Version")]')[0]
      software_version = software_td.getnext().text
      info['software_version'] = software_version
      courts.append(info)
  return courts

if __name__ == '__main__':
  import json
  print json.dumps(get_all_courts())

