from concurrent.futures import ThreadPoolExecutor
import os

from lxml import html
import pylibmc
import requests

HEADERS = {
    'User-Agent': 'court-version-scraper (2.0) <audiodude@gmail.com>'
}
TIMEOUT = 20
WORKERS = 10

def fetch_court_info(info):
  info_resp = requests.get(info['info_link'], headers=HEADERS, timeout=TIMEOUT)
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
  return info

def get_all_courts(force=False):
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
                      headers=HEADERS, timeout=TIMEOUT)
  root = html.fromstring(resp.text)

  all_courts = {}

  for tag, (name, marker) in name_to_marker.items():
    all_courts[name] = {'id': marker, 'courts': []}

  pending = []

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

    pending.append((name, info))

  with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    infos = pool.map(fetch_court_info, [info for _, info in pending])
    for (name, _), info in zip(pending, infos):
      all_courts[name]['courts'].append(info)

  if mc:
    mc.set('all_courts', all_courts, 3 * 24 * 60 * 60)
  return all_courts

if __name__ == '__main__':
  import json
  import sys

  force = False
  if len(sys.argv) == 2 and sys.argv[1] == '-f':
    force = True

  print(json.dumps(get_all_courts(force=force)))

