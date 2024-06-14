import pathlib

from extractor import scanner, printer, utils
from . import parser


def parse(base_path: pathlib.Path, output_file: pathlib.Path) -> None:
    xml_files = scanner.scan_xml_files(base_path)

    organized_xmls = utils.organize_xmls(xml_files=xml_files)

    # target_columns = [parser.BUSINESS_NAME, parser.EIN, parser.FILING_YEAR, parser.CITY_OR_TOWN, parser.STATE_OR_PROVINCE]

    all_data: list[dict] = []

    for ein, doc_type, file_name, document in organized_xmls:
        print(f"Processing file {file_name}...")

        multiple_lines = parser.extract_people_data(document)

        if multiple_lines is not None:
            all_data.extend(multiple_lines)

    printer.to_csv(data=all_data, target_file=output_file)
