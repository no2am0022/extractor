import pathlib
import typing
from xml.dom.minidom import Node, Document, parse

def read_xml(file_path: pathlib.Path):
    print(f"Parsing {file_path}")

    with open(file_path, "r") as f:
        return parse(f)


def organize_xmls(xml_files: list[str]) -> typing.Generator[tuple[str, str, str, Document], None, None]:
    for xml_file in xml_files:
        document = read_xml(xml_file)

        ein = extract_ein(document)
        document_type = extract_file_type(document)

        yield ein, document_type, xml_file, document


def extract_ein(root_element: Document) -> str:
    header_element = extract_header(root_element)
    filer_element = extract_single_tag(header_element, "Filer")
    return extract_single_tag_value(filer_element, "EIN")


def extract_header(root_element: Document) -> Document:
    return_element = extract_single_tag(root_element, "Return")
    return extract_single_tag(return_element, "ReturnHeader")


def extract_file_type(root_element: Document) -> str:
    header_element = extract_header(root_element)
    return extract_single_tag_value(header_element, "ReturnTypeCd")


def extract_single_tag(parent: Document, tag_name: str, optional: bool = False) -> Document:
    """
    Returns a direct chile element of given name
    """
    all_elements = []
    for node in parent.childNodes:
        if node.nodeType == Node.ELEMENT_NODE and node.tagName == tag_name:
            all_elements.append(node)

    if len(all_elements) == 0 and optional:
        return None

    # for elements that have more than one:
        # create an if statement that takes the first or the most relevant once and ignores the rest
    assert len(all_elements) == 1
    return all_elements[0]


def extract_single_tag_value(
    parent: Document, tag_name: str, optional: bool = False) -> str:
    element = extract_single_tag(parent, tag_name, optional=optional)
                                 
    if element is None and optional:
        return "" # returns empty strign if element is not found

    return element.firstChild.nodeValue


def extract_tag_instances(parent: Document, tag_name: str) -> list[Document]:
    """
    Returns a list of all the children nodes (of the given tag name) recursively anywhere under parent
    """
    return parent.getElementsByTagName(tag_name)


def format_address(address_element: Document) -> str:
    address = ""

    if address_element.nodeName == "RecipientUSAddress":
        # Format US address 
        numeral_address = extract_single_tag_value(address_element, "AddressLine1Txt")
        city_name = extract_single_tag_value(address_element, "CityNm")
        state = extract_single_tag_value(address_element, "StateAbbreviationCd")
        zipcode = extract_single_tag_value(address_element, "ZIPCd")

        address = f"{numeral_address}, {city_name}, {state} {zipcode}"

    elif address_element.nodeName == "RecipientForeignAddress":
        # Format foreign address
        numeral_address = extract_single_tag_value(address_element, "AddressLine1Txt")
        city_name = extract_single_tag_value(address_element, "CityNm", optional=True)
        state = extract_single_tag_value(address_element, "ProvinceOrStateNm", optional=True)
        country_code = extract_single_tag_value(address_element, "CountryCd")

        address += numeral_address + ", "

        if city_name:
            address += city_name + ", "

        if state:
            address += state + ", "

        address += country_code

    return address 
