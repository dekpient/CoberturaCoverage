import xml.etree.ElementTree as ET


def parse_files(file_names):
    files = {}
    [files.update(parse_file(file_name)) for file_name in file_names]
    return files


def parse_file(file_name):
    tree = ET.parse(file_name)
    root = tree.getroot()
    files = {}
    for cls in root.findall('./packages/package/classes/class'):
        file_attrib = cls.attrib
        file_name = file_attrib.pop('filename')
        lines = {}
        for line in cls.findall('lines/line'):
            line_attrib = line.attrib
            line_no = line_attrib.pop('number')
            lines[line_no] = line_attrib
        files[file_name] = file_attrib
        files[file_name]['lines'] = lines
    return files
