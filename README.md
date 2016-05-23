# CoberturaCoverage

This is a [Sublime Text](http://www.sublimetext.com) plugin that makes displaying lines of code not covered by a test using Cobertura reports.

## Features

* Syntax highlighting
* Including multiple files
* Stripping file name parts to match the path your tests run in

## Install

Through [Package Control](https://sublime.wbond.net/packages/Package%20Control) (recommended):

`Command Palette` > `Package Control: Install Package` > `CoberturaCoverage`

## Configuration

`Preferences` > `CoberturaCoverage` > `Settings – User`

* `coverage_on_load` - Display coverage on load, defaults to False
* `coverage_report_locations` - This is a fully qualified path to your report .xml files
* `strip_locations` - A list of locations which to remove from the beginning of a coverage report's filename. An example is:
 * I run my coverage reports in /home/jeffrand/tested_code, which may not show up in the coverage report's file names, but will be in my path as its opened in sublime, so I want to strip that location from the file's name

 ## Usage

 There is not default command for toggling CoberturaCoverage. Set you own like this:
 ```
 [
   { "keys": ["ctrl+shift+n"], "command": "toggle_coverage_report" }
 ]
 ```

