import os

from lxml import html
import pylibmc
import requests

try:
  servers = os.environ.get('MEMCACHIER_SERVERS', '').split(',')
  user = os.environ.get('MEMCACHIER_USERNAME', '')
  passwd = os.environ.get('MEMCACHIER_PASSWORD', '')
  mc = pylibmc.Client(servers, binary=True,
                      username=user, password=passwd)
except:
  mc = None

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
  all_courts = None
  if mc:
    all_courts = mc.get('all_courts')
  if all_courts:
    return all_courts

  COURT_MARKERS = ('APCTS', 'DCCTS', 'BKCTS')

  resp = requests.get('https://www.pacer.gov/psco/cgi-bin/links.pl')
  root = html.fromstring(resp.text)

  all_courts = []
  for marker in COURT_MARKERS:
    for info in get_courts(root, marker):
      info_resp = requests.get(info['info_link'])
      info_root = html.fromstring(info_resp.text)
      software_td = info_root.xpath(
        '//td[contains(text(), "Software Version")]')[0]
      software_version = software_td.getnext().text
      info['software_version'] = software_version
      all_courts.append(info)

  if mc:
    mc.set('all_courts', all_courts, 43200)  # Cache for 12 hours
  return all_courts

if __name__ == '__main__':
  import json
  print json.dumps(get_all_courts())

