# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sublime
from sublime_plugin import (TextCommand, EventListener)

from .lib import git_mixin
from .lib import json_report

BRANCH_REGION_NAME = 'IstanbulCoverage-Branch'
FUNC_REGION_NAME = 'IstanbulCoverage-Function'
STMT_REGION_NAME = 'IstanbulCoverage-Statement'
STATUS_KEY = 'IstanbulCoverage-Status'

NO_FILL = sublime.DRAW_NO_FILL
NO_OUTLINE = sublime.DRAW_NO_OUTLINE

# https://github.com/istanbuljs/istanbuljs/blob/master/packages/istanbul-lib-instrument/src/visitor.js
BRANCH_DESCRIPTIONS = {
    'default-arg': 'Default argument',
    'binary-expr': 'Logical expression',
    'cond-expr': 'Ternary expression',
    'if': 'If statement',
    'switch': 'Switch statement',
}

settings = None

# branch_type => regions
# func_name => regions
# statement_regions
FILE_TO_BRANCH_REGIONS, FILE_TO_FUNC_REGIONS, FILE_TO_STMT_REGIONS = {}, {}, {}

def plugin_loaded():
    global settings
    settings = sublime.load_settings('IstanbulCoverage.sublime-settings')

class BaseCoverage(git_mixin.GitMixin):
    def remove_regions(self, view):
        view.erase_regions(BRANCH_REGION_NAME)
        view.erase_regions(FUNC_REGION_NAME)
        view.erase_regions(STMT_REGION_NAME)

    def render_coverage(self, view):
        file_name = view.file_name()
        if not file_name:
            return

        git_repo = self.determine_git_repo(file_name)
        if not git_repo:
            sublime.status_message('Not a Git project')
            return

        report_path = os.path.join(git_repo, settings.get('coverage_local_path'))
        if not os.path.exists(report_path):
            sublime.status_message('No coverage data')
            return

        print('Rendering coverage for %s' % file_name)

        global FILE_TO_BRANCH_REGIONS, FILE_TO_FUNC_REGIONS, FILE_TO_STMT_REGIONS

        branch_regions_dict = json_report.get_branches(view, report_path, file_name)
        FILE_TO_BRANCH_REGIONS[file_name] = branch_regions_dict
        func_regions_dict = json_report.get_functions(view, report_path, file_name)
        FILE_TO_FUNC_REGIONS[file_name] = func_regions_dict
        stmt_regions = json_report.get_statements(view, report_path, file_name)
        FILE_TO_STMT_REGIONS[file_name] = stmt_regions

        self.remove_regions(view)
        branch_scope = settings.get('missing_branch_scope_name', 'invalid')
        uncovered_scope = settings.get('uncovered_scope_name', 'invalid')

        if branch_regions_dict:
            view.add_regions(BRANCH_REGION_NAME, sum(branch_regions_dict.values(), []), branch_scope, '', NO_OUTLINE)
        if func_regions_dict:
            view.add_regions(FUNC_REGION_NAME, sum(func_regions_dict.values(), []), uncovered_scope, '', NO_FILL)
        if stmt_regions:
            view.add_regions(STMT_REGION_NAME, stmt_regions, uncovered_scope, '', NO_OUTLINE)

class ToggleCoverageReportCommand(BaseCoverage, TextCommand):
    def run(self, edit):
        settings.set('coverage_on_load', not settings.get('coverage_on_load'))
        print('Toggling coverage_on_load to %s' % settings.get('coverage_on_load'))
        if settings.get('coverage_on_load'):
            self.render_coverage(self.view)
        else:
            self.remove_regions(self.view)


class CoverageReportEventListener(BaseCoverage, EventListener):
    def on_activated_async(self, view):
        if settings.get('coverage_on_load'):
            self.render_coverage(view)

    def on_close(self, view):
        file_name = view.file_name()
        if file_name in FILE_TO_BRANCH_REGIONS:
            del FILE_TO_BRANCH_REGIONS[file_name]
        if file_name in FILE_TO_FUNC_REGIONS:
            del FILE_TO_FUNC_REGIONS[file_name]
        if file_name in FILE_TO_STMT_REGIONS:
            del FILE_TO_STMT_REGIONS[file_name]

    def on_hover(self, view, point, hover_zone):
        if hover_zone is not sublime.HOVER_TEXT:
            return

        file_name = view.file_name()
        found = False
        coverage_summary = []

        if file_name in FILE_TO_BRANCH_REGIONS:
            branch_regions = FILE_TO_BRANCH_REGIONS[file_name]
            for branch_type, regions in branch_regions.items():
                if any(region.contains(point) for region in regions):
                    coverage_summary.append('<li>Branch not covered (%s)</li>' % BRANCH_DESCRIPTIONS[branch_type])
                    found = True
                    break

        if file_name in FILE_TO_FUNC_REGIONS:
            func_regions = FILE_TO_FUNC_REGIONS[file_name]
            for func_name, regions in func_regions.items():
                if any(region.contains(point) for region in regions):
                    coverage_summary.append('<li>Function "%s" not covered</li>' % func_name)
                    found = True
                    break

        if file_name in FILE_TO_STMT_REGIONS:
            stmt_regions = FILE_TO_STMT_REGIONS[file_name]
            if any(region.contains(point) for region in stmt_regions):
                coverage_summary.append('<li>Statement not covered</li>')
                found = True

        if found:
            view.show_popup(
                "<ul>" + ''.join(coverage_summary) + "</ul>",
                flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                location=point,
                max_height=300,
                max_width=view.viewport_extent()[0]
            )
            view.set_status(STATUS_KEY, 'Missing coverage')
        else:
            view.erase_status(STATUS_KEY)
