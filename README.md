# Sublime Istanbul Coverage

This is a [Sublime Text](http://www.sublimetext.com) plugin that highlights sections of code not covered by tests from Istanbul's JSON report.

## Requirements

* Only works in a Git project. Easy if all your projects put generated coverage reports in same location.

## Features

* Precise highlights of missing branches, functions and statements
* Show a tooltip popup and set status bar message on hover
* Allow changing scope name for customizable highlight colors

## Install

_TODO:_ Through [Package Control](https://sublime.wbond.net/packages/Package%20Control):

`Command Palette` > `Package Control: Install Package` > `IstanbulCoverage`

Or manually clone the repo:

```sh
cd "~/Library/Application Support/Sublime Text 3/Packages"
git clone --depth 1 https://github.com/dekpient/sublime-istanbul-coverage.git IstanbulCoverage
```

## Configuration

`Preferences` > `IstanbulCoverage` > `Settings – User`

* `coverage_on_load` - Display coverage on load, defaults to False
* `coverage_local_path` - This is a local path from the root of your Git project to your report .json file, defaults to `coverage/coverage-final.json`
* `uncovered_scope_name` - Defaults to `invalid.illegal`
* `missing_branch_scope_name` - Defaults to `invalid.unimplemented`

## Usage

`Command Palette` > `Toggle Coverage Report`

Or add your own key binding in `Preferences` > `Key Bindings` e.g.

```json
[
  { "keys": ["super+t", "super+c"], "command": "toggle_coverage_report" }
]
```
