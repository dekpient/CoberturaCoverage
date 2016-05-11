# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import xml.etree.ElementTree as ET


def parse_reports(report_names, source_files, source_report_mapping, report_mtimes):
    print(source_files.keys())
    for report_name in report_names:
        try:
            mtime = os.path.getmtime(report_name)
        except OSError:
            pass
        else:
            if mtime > report_mtimes.get(report_name, 0):
                # store mtime
                report_mtimes[report_name] = mtime
                # get parsed files
                _source_files = parse_report(report_name)
                # remove previously mapped files
                for k in source_report_mapping.get(report_name, []):
                    source_files.pop(k, None)
                # map current file report sources
                source_report_mapping[report_name] = _source_files.keys()
                source_files.update(_source_files)
    return source_files


def parse_report(report_name):
    source_files = {}
    try:
        tree = ET.parse(report_name)
    except OSError:
        pass
    else:
        root = tree.getroot()
        for cls in root.findall('./packages/package/classes/class'):
            file_attrib = cls.attrib
            file_name = file_attrib.pop('filename')
            lines = {}
            for line in cls.findall('lines/line'):
                line_attrib = line.attrib
                line_no = line_attrib.pop('number')
                lines[line_no] = line_attrib
            source_files[file_name] = file_attrib
            source_files[file_name]['lines'] = lines
    return source_files
