#!/usr/bin/env python3
import json, pyquery
import os.path as p

class FlagsGenerator(object):

    def __init__(self):
        self.url = None # type: str

    def collect_page_flags(self, url):
        items = []
        for it in pyquery.PyQuery(url).find('#countries article'):
            href = it.xpath('./h2/a/@href')[0] # type: str
            icon = it.xpath('./div/a/img/@src')[0] # type: str
            items.append(
                {
                    'id': p.basename(href),
                    'name': it.xpath('./h2/a/text()')[0],
                    'link': self.url + href,
                    'icon': icon,
                    'size': [int(it.xpath('./div/a/img/@width')[0]), int(it.xpath('./div/a/img/@height')[0])],
                    'abbr': p.basename(icon).split('.')[0]
                }
            )
        return items

    def generate_category(self, cate):
        group = []
        data = []
        for a in cate.xpath('./div/a'):
            href = a.get('href')
            link = self.url + href
            group.append({'id': p.basename(href), 'name': a.text, 'link': link})
            data.append(self.collect_page_flags(url=link))
        return {'cate': group, 'data': data}

    def load(self, url:str):
        self.url = url
        page = pyquery.PyQuery(url)
        data = {}
        for cate in page.find('#sidebar nav .box'):
            path = cate.xpath('./h3/a/@href')[0] # type: str
            if path.endswith('continent') or path.endswith('organization'):
                data[p.basename(path)] = self.generate_category(cate)

        return data

def main():
    flags = FlagsGenerator()
    foreign_data = flags.load(url='http://flagpedia.net')
    chinese_data = flags.load(url='http://flagpedia.asia')
    for type, data in foreign_data.items():
        _data = chinese_data.get(type)
        items = data.get('data') # type: list[list]
        _items = _data.get('data') # type: list[list]
        for n in range(len(items)):
            subs = items[n]
            _subs = _items[n]
            assert len(subs) == len(_subs)
            for i in range(len(subs)):
                it = subs[i]
                _it = _subs[i]
                it['desc'] = _it['name']
    print(json.dumps(foreign_data, ensure_ascii=False, indent=4))



if __name__ == '__main__':
    main()