#!/usr/bin/env python3
import json, pyquery, xlwt
import os.path as p

class FlagsGenerator(object):

    def __init__(self):
        self.url = None # type: str
        self.map = {} # type: dict[int, dict]

    def collect_page_flags(self, url, cate_label, cate_value, exclusive = False):
        for it in pyquery.PyQuery(url).find('#countries article'):
            icon = it.xpath('./div/a/img/@src')[0] # type: str
            abbr = p.basename(icon).split('.')[0] # type: str
            id = ord(abbr[0]) << 8 | ord(abbr[1])
            if id in self.map:
                data = self.map.get(id)
            else:
                self.map[id] = data = {'id': id, 'name': it.xpath('./h2/a/text()')[0], 'abbr': abbr}
            if not exclusive:
                if cate_label not in data:
                    data[cate_label] = []
                data[cate_label].append(cate_value)
            else:
                data[cate_label] = cate_value

    def generate_category(self, cate, label, exclusive):
        for a in cate.xpath('./div/a'):
            link = self.url + a.get('href')
            self.collect_page_flags(url=link, cate_label=label, cate_value=a.text, exclusive=exclusive)

    def load(self, url:str):
        self.url = url
        page = pyquery.PyQuery(url)
        for cate in page.find('#sidebar nav .box'):
            path = cate.xpath('./h3/a/@href')[0] # type: str
            if path.endswith('continent'):
                self.generate_category(cate, label=p.basename(path), exclusive=True)
            elif path.endswith('organization'):
                self.generate_category(cate, label=p.basename(path), exclusive=False)
        data = []
        for _, it in self.map.items():
            data.append(it)
        from operator import itemgetter
        data.sort(key=itemgetter('id'))
        return data

def main():
    flags = FlagsGenerator()
    foreign_data = flags.load(url='http://flagpedia.net')
    flags = FlagsGenerator()
    chinese_data = flags.load(url='http://flagpedia.asia')
    for n in range(len(foreign_data)):
        it = foreign_data[n]
        _it= chinese_data[n]
        it['note'] = _it['name']
        org = it.get('organization') # type: list[str]
        it['show'] = 1 if org and 'European Union' in org else 0
        it['gdpr'] = it['show']
    book = xlwt.Workbook()
    sheet = book.add_sheet(sheetname='COUNTRY_CONF')
    field_names = ('id', 'name', 'show', 'gdpr', 'abbr', 'note', 'continent', 'organization')
    field_notes = ('ID', '国家英文名', '是否可选', '执行欧盟规范', '国家两字母缩写', '国家说明', '国家所属大洲', '国家所属国际组织')
    field_types = ('uint32', 'string', 'bool', 'bool') + ('string',)*4
    field_rules = ('required',)*7 + ('repeated',)

    field_count = len(field_names)
    for n in range(field_count):
        sheet.write(0, n, field_rules[n])
    for n in range(len(field_names)):
        sheet.write(1, n, field_types[n])
    for n in range(field_count):
        sheet.write(2, n, field_names[n])
    for n in range(field_count):
        sheet.write(3, n, 'client')
    for n in range(field_count):
        sheet.write(4, n, field_notes[n])
    for n in range(len(foreign_data)):
        r = n + 5
        it = foreign_data[n]
        for c in range(field_count):
            name = field_names[c]
            if c == field_count - 1:
                if name in it: sheet.write(r, c, ';'.join(it.get(name)))
            else:
                sheet.write(r, c, it.get(name))
    book.save('country.xls')
    print(json.dumps(foreign_data, ensure_ascii=False, indent=4))



if __name__ == '__main__':
    main()