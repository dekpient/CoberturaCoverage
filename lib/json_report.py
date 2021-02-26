import json
import os
import sublime

from . import util

REPORTS = {}
REPORT_MTIMES = {}

def load_report(report_path):
    global REPORTS, REPORT_MTIMES
    try:
        mtime = os.path.getmtime(report_path)
    except OSError:
        return
    else:
        if mtime > REPORT_MTIMES.get(report_path, 0) or report_path not in REPORTS:
            with open(report_path) as f:
                REPORTS[report_path] = json.load(f)
    return REPORTS[report_path]

def load_coverage(report_path, file_name):
    report = load_report(report_path)
    if not report or file_name not in report:
        print("No report for %s" % file_name)
        return
    return report[file_name]

def gen_region(view, start_location, end_location):
    return sublime.Region(
        # column can be null
        view.text_point(start_location['line'] - 1, start_location['column'] or 1),
        view.text_point(end_location['line'] - 1, end_location['column'] or 1)
    )

def get_branches(view, report_path, file_name):
    coverage_data = load_coverage(report_path, file_name)
    if not coverage_data:
        return;

    branch_regions_by_type = dict()
    for branch_key in coverage_data['b']:
        branch_coverage = coverage_data['b'][branch_key]
        for i in range(len(branch_coverage)):
            if branch_coverage[i] > 0:
                continue

            branch_detail = coverage_data['branchMap'][branch_key]
            branch_type = branch_detail['type']
            loc = branch_detail['locations'][i]

            regions = branch_regions_by_type.setdefault(branch_type, [])
            regions.append(gen_region(view, loc['start'], loc['end']))

    return branch_regions_by_type

def get_functions(view, report_path, file_name):
    coverage_data = load_coverage(report_path, file_name)
    if not coverage_data:
        return;

    func_regions_by_name = dict()
    for func_key in coverage_data['f']:
        func_coverage = coverage_data['f'][func_key]
        if func_coverage > 0:
            continue

        func_detail = coverage_data['fnMap'][func_key]
        func_name = func_detail['name']
        decl = func_detail['decl']
        loc = func_detail['loc']

        regions = func_regions_by_name.setdefault(func_name, [])
        regions.append(gen_region(view, decl['start'], loc['end']))

    return func_regions_by_name

def get_statements(view, report_path, file_name):
    coverage_data = load_coverage(report_path, file_name)
    if not coverage_data:
        return;

    statements_regions = []
    for stmt_key in coverage_data['s']:
        stmt_coverage = coverage_data['s'][stmt_key]
        if stmt_coverage > 0:
            continue

        stmt_detail = coverage_data['statementMap'][stmt_key]
        loc = stmt_detail

        statements_regions.append(gen_region(view, loc['start'], loc['end']))

    return statements_regions
