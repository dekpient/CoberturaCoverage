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

LIST_POPUP = """
<style>
body {
    margin: 0px;
}
div {
    border: 1px;
    padding-right: 30px;
    border-style: solid;
    border-color: #FFA500FF;
}
</style>
<body>
<div>
<ul>
%s
</ul>
</div>
</body>
"""

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
        first_folder = view.window().folders()[0]
        root_dir = git_repo or first_folder
        if not root_dir:
            return

        report_path = os.path.join(root_dir, settings.get('coverage_local_path'))
        if not os.path.exists(report_path):
            sublime.status_message('No coverage report')
            return

        # print('Rendering coverage for %s' % file_name)

        global FILE_TO_BRANCH_REGIONS, FILE_TO_FUNC_REGIONS, FILE_TO_STMT_REGIONS
        success, branch_regions_dict, func_regions_dict, stmt_regions = json_report.get_uncovered_regions(view, report_path, file_name)
        if not success:
            return

        FILE_TO_BRANCH_REGIONS[file_name] = branch_regions_dict
        FILE_TO_FUNC_REGIONS[file_name] = func_regions_dict
        FILE_TO_STMT_REGIONS[file_name] = stmt_regions

        branch_scope = settings.get('missing_branch_scope_name', 'invalid')
        uncovered_scope = settings.get('uncovered_scope_name', 'invalid')

        self.remove_regions(view)
        view.add_regions(BRANCH_REGION_NAME, sum(branch_regions_dict.values(), []), branch_scope, '', NO_OUTLINE)
        view.add_regions(FUNC_REGION_NAME, sum(func_regions_dict.values(), []), uncovered_scope, '', NO_FILL)
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
        FILE_TO_BRANCH_REGIONS.pop(file_name, None)
        FILE_TO_FUNC_REGIONS.pop(file_name, None)
        FILE_TO_STMT_REGIONS.pop(file_name, None)

    def is_point_in_regions(self, point, regions):
        return any(region.contains(point) for region in regions)

    def get_uncovered_point_desc(self, point, file_name, regions_map):
        if file_name not in regions_map:
            return
        regions_data = regions_map[file_name]
        for key, regions in regions_data.items():
            if self.is_point_in_regions(point, regions):
                return key
        return None

    def on_hover(self, view, point, hover_zone):
        if hover_zone is not sublime.HOVER_TEXT:
            return

        file_name = view.file_name()
        found = False
        coverage_summary = []

        missed_branch_type = self.get_uncovered_point_desc(point, file_name, FILE_TO_BRANCH_REGIONS)
        if missed_branch_type:
            coverage_summary.append('<li>Branch not covered (%s)</li>' % BRANCH_DESCRIPTIONS[missed_branch_type])
            found = True

        missed_func_name = self.get_uncovered_point_desc(point, file_name, FILE_TO_FUNC_REGIONS)
        if missed_func_name:
            coverage_summary.append('<li>Function "%s" not covered</li>' % missed_func_name)
            found = True

        if file_name in FILE_TO_STMT_REGIONS and self.is_point_in_regions(point, FILE_TO_STMT_REGIONS[file_name]):
            coverage_summary.append('<li>Statement not covered</li>')
            found = True

        if found:
            view.show_popup(
                LIST_POPUP % ''.join(coverage_summary),
                flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                location=point,
                max_height=300,
                max_width=view.viewport_extent()[0]
            )
            view.set_status(STATUS_KEY, 'Missing coverage')
        else:
            view.erase_status(STATUS_KEY)
