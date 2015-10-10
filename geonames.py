#!/usr/bin/env python3.4
import bs4, csv, signal, sys
from urllib import request, parse
from copy import copy, deepcopy
from collections import OrderedDict
from geonames.Row import Row

countries='http://www.geonames.org/countries/'

def getRegionUrl(url):
    body = request.urlopen(url).read()
    doc = bs4.BeautifulSoup(body)
    if bs4.__version__ < '4.4.0':
        a = doc.find('a', text='Administrative Division')
    else:
        a = doc.find('a', string='Administrative Division')
    return parse.urljoin(url, a['href'])

def getRegionData(co, url):
    body = request.urlopen(url).read()
    doc = bs4.BeautifulSoup(body)
    data = []
    fields = OrderedDict.fromkeys(['country'])
    for table in [x for x in doc('table', 'restable') if 'subdivtable' in x['id']]:
        rows = table('tr')
        template = Row(rows.pop(0))
        template.default = None
        template.stringify = True
        fields.update(template.fields)
        for row in rows:
            region = copy(template)
            region.data = row
            region.data['country'] = co
            data.append(region)
    return (data, fields)

def scrape(entrance, limit=None, ignore=['', 'iso region', 'capital', 'population', 'area in km²', 'lang', 'continent', 'from', 'till']):
    def report(signum, frame):
        print("co:", country['Country'].text, file=sys.stderr)
    body = request.urlopen(entrance).read()
    doc = bs4.BeautifulSoup(body)
    countries = doc.select('table#countries tr')
    country = Row(countries.pop(0))
    regions = []
    fields = OrderedDict()
    signal.signal(signal.SIGINFO, report)
    for row in countries:
        if limit:
            limit -= 1
        elif 0 == limit:
            break
        country.data = row
        coUrl = parse.urljoin(entrance, country['Country'].a['href'])
        url = getRegionUrl(coUrl)
        (data, rgnFields) = getRegionData(country['ISO-3166alpha2'].text, url)
        regions += data
        fields.update(rgnFields)
    signal.signal(signal.SIGINFO, signal.SIG_DFL)
    for field in ignore:
        if field in fields:
            del fields[field]
    fields['name of subdivision'] = 'name'
    return (regions, fields)

(regions, fields) = scrape(countries, 2)
out = csv.DictWriter(sys.stdout, fieldnames=fields.keys(), extrasaction='ignore')
out.writeheader()
out.writerows(regions)
