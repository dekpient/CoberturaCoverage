# -*- coding: utf-8 -*-
from __future__ import print_function

import sublime
from sublime_plugin import TextCommand

from .lib.parse_reports import parse_files

GOOD_REGION_NAME = 'CoberturaCoverage-Good'
BAD_REGION_NAME = 'CoberturaCoverage-Bad'
FILL = sublime.DRAW_NO_FILL
settings = None

FILES = {}


def plugin_loaded():
    global settings
    settings = sublime.load_settings('CoberturaCoverage.sublime-settings')


class BaseCoverage(TextCommand):
    def get_region_name(self, present=False):
        return GOOD_REGION_NAME if present else BAD_REGION_NAME

    def remove_regions(self, view, present=False):
        region = self.get_region_name(present=present)
        view.erase_regions(region)


class RemoveCoverageReportCommand(BaseCoverage):
    def run(self, edit):
        self.remove_regions(self.view, present=False)
        self.remove_regions(self.view, present=True)


class LoadCoverageReportCommand(BaseCoverage):
    def run(self, edit):
        files = parse_files(settings.get('coverage_report_locations'))
        file_name = self.view.file_name()
        for loc in settings.get('strip_locations', []):
            if file_name.startswith(loc):
                file_name = file_name.replace(loc, '')
                break

        file_data = files.get(file_name)
        if file_data:
            covered, uncovered = self.filter_lines(file_data['lines'])
            self.remove_regions(self.view, present=False)
            self.remove_regions(self.view, present=True)
            self.highlight_lines(self.view, uncovered, present=False)

    def filter_lines(self, lines):
        covered, uncovered = [], []
        for k, v in lines.items():
            k = int(k)
            if 'condition-coverage' in v and '100%' in v['condition-coverage']:
                covered.append(k)
            elif v['hits'] == '1':
                covered.append(k)
            else:
                uncovered.append(k)
        return covered, uncovered

    def highlight_lines(self, view, _lines, present=False):
        region = self.get_region_name(present=present)
        lines = [view.line(view.text_point(line_num - 1, 0)) for line_num in _lines]
        self.remove_regions(view, present=present)
        if lines:
            view.add_regions(region, lines, "markup" if present else "invalid", '', FILL)
