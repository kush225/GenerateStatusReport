#!/usr/bin/python
# -*- coding: utf-8 -*-

import markup
import argparse
import csv

HEADERS = ['Category', 'Total', 'Passed', 'Failed']
is_header_in_file = True
(failed_cases, passed_cases) = ([], [])

minified_css = \
    '.container,table,td,th{border:1px solid #e0e0e0}body,th{color:#333}body{font-size:.9rem}.container{width:90%;padding:50px}table{border-collapse:collapse;width:80%}table,td,th{padding:10px;font-size:1em}th{background-color:#f5f5f5;text-align:left}.divider{border-top:1px solid #e0e0e0}.signature{color:#607d8b}.lead{font-size:1.68rem;color:#616161;font-weight:300}'

feature_map = {}

def generate_htmlpage(
    start_time,
    end_time,
    category,
    release,
    version,
    tabledata=[],
    ):

    page = markup.page()
    page.init(title='%s Report' % category, doctype='<!DOCTYPE html>')
    page.div(_class='container')
    page.table(style='width: 92% !important; border: 0px;')
    page.tr()
    page.td(width='30%',
            style='border: 0px!important; padding: 0px!important')
    page.h2('{} Test Report'.format(category.capitalize()),
            _class='lead')
    page.td.close()
    page.td(width='70%',
            style='border: 0px!important; padding: 0px!important')
    page.table()
    page.tr()
    page.th('Status')
    page.th('Start Time')
    page.th('End Time')
    page.tr.close()
    page.tr()
    if len(failed_cases) > 0:
        page.td('Failed', style='background-color: #FFCCCC')
    else:
        page.td('Passed', style='background-color: #E8F5E9')
    page.td(start_time)
    page.td(end_time)
    page.tr.close()
    page.table.close()
    page.td.close()
    page.tr.close()
    page.table.close()
    page.br()
    page.div(_class='divider')
    page.br()

    page.table()
    page.caption(f'{category.capitalize()} Results', _class='lead')

    page.tr()
    for header in HEADERS:
        page.th(header)
    page.tr.close()

    page.tr()
    for data in tabledata:
        page.td(data)
    page.tr.close()

    page.table.close()
    for i in range(3):
        page.br()
    page.table()
    page.caption('Performance Stats Report', _class='lead')
    page.tr()
    page.th('Name')
    page.th('Category')
    page.th('Total')
    page.th('Passed', width='10%')
    page.th('Failed')
    page.tr.close()
    for feature in feature_map:
        for group in feature_map[feature]:
            page.tr()
            page.td(feature)
            page.td(group)
            page.td(feature_map[feature][group]['total'],
                    style='color: blue; font-weight: bold')
            page.td(feature_map[feature][group]['passed'],
                    style='color: green; font-weight: bold')
            page.td(feature_map[feature][group]['failed'],
                    style='color: red; font-weight: bold')
            page.tr.close()
    page.table.close()

    for i in range(3):
        page.br()
    if len(failed_cases) > 0:
        page.table()
        page.caption('Failed Cases', _class='lead')
        page.tr()
        page.th('Name')
        page.th('Category')
        page.th('TestRun', width='10%')
        page.th('Description')
        page.tr.close()
        for cases in failed_cases:
            page.tr()
            page.td(cases.get('name'))
            page.td(cases.get('category'))
            page.td(cases.get('testrun'))
            page.td(cases.get('description'))
            page.tr.close()
        page.table.close()
    for i in range(3):
        page.br()
    page.a('Click to see online reports',
           href='http://10.0.0.0/reports/%s/%s/B%s'
            % (category.lower(), release, version),
           style='text-decoration: none; color: #263238;')
    for i in range(2):
        page.br()

    page.div('XYZ Team <br/>ABC private limited.',
             _class='signature')
    page.div.close()
    page.style(minified_css)
    htmlpage = str(page)
    return htmlpage


def parse_results_file(f):
    data = []
    with open(f, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
        
    for line in data:
        hash_data = dict(line)
        name, category, testrun, status, description  = [v[1] for v in hash_data.items()]
        
        if not name in feature_map:
            feature_map[name] = {}

        if not category in feature_map[name]:
            feature_map[name][category] = {}

        if not 'total' in feature_map[name][category]:
            feature_map[name][category]['total'] = 0
        if not 'failed' in feature_map[name][category]:
            feature_map[name][category]['failed'] = 0
        if not 'passed' in feature_map[name][category]:
            feature_map[name][category]['passed'] = 0

        if status == 'fail':
            failed_cases.append(hash_data)
            feature_map[name][category]['failed'] += 1
        else:

            passed_cases.append(hash_data)
            feature_map[name][category]['passed'] += 1

        feature_map[name][category]['total'] += 1


def gettabledata(category):
    failed_count = len(failed_cases)
    passed_count = len(passed_cases)
    total = passed_count + failed_count
    return (category.upper(), total, passed_count, failed_count)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--category', help='the category',
                        default='SMOKE')
    parser.add_argument('-r', '--release', help='the release name',
                        required=True)
    parser.add_argument('-v', '--version', help='the build version',
                        required=True)
    parser.add_argument('-f', '--infile', help='the result file',
                        required=True)
    parser.add_argument('-o', '--outfile',
                        help='the outfile to write to',
                        default='/tmp/output.html')
    parser.add_argument('-s', '--starttime', help='The startime',
                        required=True)
    parser.add_argument('-e', '--endtime', help='The endtime',
                        required=True)
    opts = parser.parse_args()

    parse_results_file(opts.infile)
    tabledata = gettabledata(opts.category)
    start_time = opts.starttime
    end_time = opts.endtime

    with open(opts.outfile, 'w') as outfile:
        outfile.write(generate_htmlpage(
            start_time,
            end_time,
            opts.category,
            opts.release,
            opts.version,
            tabledata,
            ))

