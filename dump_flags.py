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

def dump_missing(item_list, check_list):
    check_map = {}
    for it in check_list:
        check_map[it] = it
    missing_list = []
    for it in item_list:
        if it not in check_map: missing_list.append(it)
    print(missing_list)

def main():
    flags = FlagsGenerator()
    foreign_data = flags.load(url='http://flagpedia.net')
    flags = FlagsGenerator()
    chinese_data = flags.load(url='http://flagpedia.asia')
    show_list = ['匈牙利', '希腊', '意大利', '列支敦斯登', '土耳其', '圣马力诺', '英国', '挪威', '爱尔兰岛', '爱沙尼亚', '丹麦', '喬治亞', '阿塞拜疆',
                 '阿尔巴尼亚', '克罗地亚', '乌克兰', '羅馬尼亞', '瑞典', '瑞士', '塞尔维亚', '賽普勒斯', '葡萄牙', '卢森堡', '奥地利', '摩尔多瓦', '摩纳哥', '马耳他',
                 '捷克', '荷兰', '白俄罗斯', '西班牙', '安道尔', '亞美尼亞', '芬兰', '斯洛伐克', '斯洛文尼亚', '冰岛', '梵蒂冈', '德国', '俄罗斯', '拉脫維亞',
                 '立陶宛', '蒙特內哥羅', '比利时', '法国', '保加利亚', '波兰', '波斯尼亚和黑塞哥维那']
    gdpr_list = ['匈牙利', '希腊', '意大利', '列支敦斯登', '挪威', '爱尔兰岛', '爱沙尼亚', '丹麦', '克罗地亚', '羅馬尼亞', '瑞典', '瑞士', '賽普勒斯', '葡萄牙',
                 '卢森堡', '奥地利', '马耳他', '捷克', '荷兰', '西班牙', '芬兰', '斯洛伐克', '斯洛文尼亚', '冰岛', '德国', '拉脫維亞', '立陶宛', '比利时',
                 '法国', '保加利亚', '波兰', '英国']
    check_show_list = []
    check_gdpr_list = []
    for n in range(len(foreign_data)):
        it = foreign_data[n]
        _it= chinese_data[n]
        it['note'] = _it['name']
        it['show'] = 1 if it['note'] in show_list else 0
        it['gdpr'] = 1 if it['note'] in gdpr_list else 0
        if it['show']: check_show_list.append(it['note'])
        if it['gdpr']: check_gdpr_list.append(it['note'])
    check_show_list.sort()
    check_gdpr_list.sort()
    if len(check_show_list) != len(show_list): dump_missing(item_list=show_list, check_list=check_show_list)
    if len(check_gdpr_list) != len(gdpr_list): dump_missing(item_list=gdpr_list, check_list=check_gdpr_list)
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