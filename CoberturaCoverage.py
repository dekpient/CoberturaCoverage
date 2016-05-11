# -*- coding: utf-8 -*-
from __future__ import print_function
from imp import reload

import sublime
from sublime_plugin import (TextCommand, EventListener)

from .lib import parse_reports

GOOD_REGION_NAME = 'CoberturaCoverage-Good'
BAD_REGION_NAME = 'CoberturaCoverage-Bad'
FILL = sublime.DRAW_NO_FILL
settings = None

SOURCE_FILES, SOURCE_REPORT_MAPPING, REPORT_MTIMES = {}, {}, {}

FILES = {}


def plugin_loaded():
    global settings
    settings = sublime.load_settings('CoberturaCoverage.sublime-settings')


class BaseCoverage(object):
    def remove_regions(self, view):
        view.erase_regions(BAD_REGION_NAME)

    def trim_file_name(self, file_name):
        for loc in settings.get('strip_locations', []):
            if file_name.startswith(loc):
                file_name = file_name.replace(loc, '')
                break
        return file_name

    def render_coverage(self, view):
        file_name = view.file_name()
        if not file_name:
            return

        global SOURCE_FILES, SOURCE_REPORT_MAPPING, REPORT_MTIMES

        reload(parse_reports)
        files = parse_reports.parse_reports(settings.get('coverage_report_locations'), SOURCE_FILES,
                                            SOURCE_REPORT_MAPPING, REPORT_MTIMES)
        file_name = self.trim_file_name(file_name)
        file_data = files.get(file_name)

        if file_data:
            covered, uncovered = self.filter_lines(file_data['lines'])
            self.remove_regions(view)
            self.highlight_lines(view, uncovered)

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

    def highlight_lines(self, view, _lines):
        region = BAD_REGION_NAME
        lines = [view.line(view.text_point(line_num - 1, 0)) for line_num in _lines]
        self.remove_regions(view)
        if lines:
            view.add_regions(region, lines, "invalid", '', FILL)


class ToggleCoverageReportCommand(BaseCoverage, TextCommand):
    def run(self, edit):
        settings.set('coverage_on_load', not settings.get('coverage_on_load'))
        print("Toggling coverage_on_load to %s" % settings.get('coverage_on_load'))
        if settings.get('coverage_on_load'):
            self.render_coverage(self.view)
        else:
            self.remove_regions(self.view)


class CoverageReportEventListener(BaseCoverage, EventListener):
    def on_activated_async(self, view):
        if settings.get('coverage_on_load'):
            self.render_coverage(view)
