import os

from lxml import html
import pylibmc
import requests

HEADERS = {
    'User-Agent': 'court-version-scraper (2.0) <audiodude@gmail.com>'
}

mc = None
try:
  servers = os.environ.get('MEMCACHIER_SERVERS', '').split(',')
  user = os.environ.get('MEMCACHIER_USERNAME', '')
  passwd = os.environ.get('MEMCACHIER_PASSWORD', '')
  if servers and user and passwd:
    mc = pylibmc.Client(servers, binary=True,
                      username=user, password=passwd)
except:
  mc = None

def get_all_courts(force=False):
  all_courts = None
  if mc:
    all_courts = mc.get('all_courts')
  if all_courts and not force:
    return all_courts

  name_to_marker = {
    'Appeals': ('U.S. Courts of Appeals', 'APCTS'),
    'District': ('U.S. District Courts', 'DCCTS'),
    'Bankruptcy': ('U.S. Bankruptcy Courts', 'BKCTS'),
  }
  COURT_MARKERS = (('U.S. Courts of Appeals', 'APCTS'),
                   ('U.S. District Courts', 'DCCTS'),
                   ('U.S. Bankruptcy Courts', 'BKCTS'))

  resp = requests.get('https://pacer.uscourts.gov/file-case/court-cmecf-lookup',
                      headers=HEADERS)
  root = html.fromstring(resp.text)

  all_courts = {}

  for tag, (name, marker) in name_to_marker.items():
    all_courts[name] = {'id': marker, 'courts': []}

  for row in root.iterfind('.//tr'):
    court_type = None
    info = {}
    for col in row.iterfind('./td'):
      klass = col.get('class')
      if 'court-name' in klass:
        anchor = col.find('./a')
        info['court'] = anchor.text.strip()
        info['info_link'] = 'https://pacer.uscourts.gov%s' % anchor.get('href')
      elif 'court-type' in klass:
        court_type = col.text.strip()
    
    name, marker = name_to_marker.get(court_type, (None, None))
    if marker is None:
      continue

    info_resp = requests.get(info['info_link'], headers=HEADERS)
    info_root = html.fromstring(info_resp.text)

    software_td = info_root.xpath(
      '//td[contains(text(), "Software Version")]')
    if software_td:
      software_td = software_td[0]
      info['software_version'] = software_td.getnext().text
    else:
      info['software_version'] = None

    go_live_td = info_root.xpath(
      '//td[contains(text(), "ECF Go Live Date")]')
    if go_live_td:
      go_live_td = go_live_td[0]
      info['software_go_live'] = go_live_td.getnext().text
    else:
      info['software_go_live'] = None

    court_header_div = info_root.xpath(
      '//i[contains(@class, "fa-globe-americas")]')
    if court_header_div:
      court_header_div = court_header_div[0].getparent().getnext()
      info['court_link'] = court_header_div.find('.//a').get('href')

    all_courts[name]['courts'].append(info)
      
  if mc:
    mc.set('all_courts', all_courts)
  return all_courts

if __name__ == '__main__':
  import json
  import sys

  force = False
  if len(sys.argv) == 2 and sys.argv[1] == '-f':
    force = True

  print(json.dumps(get_all_courts(force=force)))

