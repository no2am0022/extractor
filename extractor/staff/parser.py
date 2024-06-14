#
# Read an XML file and parse into memory
# Write a code to scan through the folder and its subfolders where the files are at.
# Extract the files to create several CSV files
#

from datetime import datetime, date
import pathlib
import typing
from xml.dom.minidom import parse, Document

from extractor import utils

# set the names for the constants which are used to hold extracted data xmls and properly arrange them
FILING_YEAR = "Filing Year"
CHARITY_EIN = "EIN"
BUSINESS_NAME = "Name of organization"
CITY_OR_TOWN = "City/Town"
STATE_OR_PROVINCE = "State/Province"
ZIPCODE = "Zip Code"
FORM_TYPE = "Type"
COUNTRY = "Country"
ADDRESS1 = "Address 1"  # changed from Number and Street (some provided only a PO Box)

def extract_common_data(dom: Document) -> dict[str, str] | None:
    data = {}

    return_element = utils.extract_single_tag(dom, "Return")
    header_element = utils.extract_single_tag(return_element, "ReturnHeader")
    filer_element = utils.extract_single_tag(header_element, "Filer")

    # Get the filing year
    tax_period_begin_text = utils.extract_single_tag_value(header_element, "TaxPeriodBeginDt")
    tax_period_begin: date = datetime.strptime(tax_period_begin_text, "%Y-%m-%d")
    data[FILING_YEAR] = tax_period_begin.year

    # get file type
    data[FORM_TYPE] = utils.extract_single_tag_value(header_element, "ReturnTypeCd")

    # Get Charity EIN
    data[CHARITY_EIN] = utils.extract_single_tag_value(filer_element, "EIN")

    # Get filer business name
    business_name_element = utils.extract_single_tag(filer_element, "BusinessName")
    data[BUSINESS_NAME] = utils.extract_single_tag_value(business_name_element, "BusinessNameLine1Txt")

    # find address section and step into it
    us_address_element = utils.extract_single_tag(filer_element, "USAddress")

    # find the filer city/town
    data[CITY_OR_TOWN] = utils.extract_single_tag_value(us_address_element, "CityNm")

    # find the filer zipcode
    data[ZIPCODE] = utils.extract_single_tag_value(us_address_element, "ZIPCd")

    # find the filer state/province
    data[STATE_OR_PROVINCE] = utils.extract_single_tag_value(us_address_element, "StateAbbreviationCd")

    # find the filer address
    data[ADDRESS1] = utils.extract_single_tag_value(us_address_element, "AddressLine1Txt")

    # set the filer address to US
    data[COUNTRY] = "US"  # If USAddress fails, we will need to change this but so far only US addresses were found 

    return data


def extract_employee_info_1(dom: Document, common_data: dict) -> list[dict[str, str]]:
    records = []
    
    employee_elements = utils.extract_tag_instances(dom, "Form990PartVIISectionAGrp")
    
    for employee_element in employee_elements:
        # Create a new record for this contractor and fill in common data
        employee_data = {**common_data}
        employee_data["Employee Type"] = "Form990PartVIISectionAGrp"

        # employee name tag = PersonNm
        employee_data["Employee Name"] = utils.extract_single_tag_value(employee_element, "PersonNm", optional=True)
        # employee title tag = TitleTxt
        employee_data["Employee Title"] = utils.extract_single_tag_value(employee_element, "TitleTxt")
        # employee compensation
        employee_data["Employee Compensation"] = utils.extract_single_tag_value(employee_element, "ReportableCompFromOrgAmt")

        records.append(employee_data)

    return records


def extract_employee_info_2(dom: Document, common_data: dict) -> list[dict[str, str]]:
    records = []
    
    employee_elements = utils.extract_tag_instances(dom, "OfficerDirectorTrusteeEmplGrp")

    for employee_element in employee_elements:
        # Create a new record for this contractor and fill in common data
        employee_data = {**common_data}
        employee_data["Employee Type"] = "OfficerDirectorTrusteeEmplGrp"
        employee_data["Employee Name"] = utils.extract_single_tag_value(employee_element, "PersonNm")
        employee_data["Employee Title"] = utils.extract_single_tag_value(employee_element, "TitleTxt")

        # Look for US address first
        employee_address_element = utils.extract_single_tag(employee_element, "RecipientUSAddress", optional=True)
        if not employee_address_element:
            # Check if we have a foreign address
            employee_address_element = utils.extract_single_tag(employee_element, "RecipientForeignAddress", optional=True)
            if not employee_address_element:
                # No address found!
                continue

        employee_data["Employee Address"] = utils.format_address(employee_address_element)
    



        # key employee type of service tag = ???
        # key employee position tag = ???
        employee_data["Employee Compensation"] = utils.extract_single_tag_value(employee_element, "CompensationAmt")
        # key employee total compensation (all staff) =

        records.append(employee_data)

    return records


def extract_employee_info_3(dom: Document, common_data: dict) -> list[dict[str, str]]:
    records = []
    
    employee_elements = utils.extract_tag_instances(dom, "OfficerDirTrstKeyEmplInfoGrp")

    for employee_element in employee_elements:
        # Create a new record for this contractor and fill in common data
        employee_data = {**common_data}
        employee_data["Employee Type"] = "OfficerDirTrstKeyEmplInfoGrp"
        # employee_data["Employee Name"] = utils.extract_single_tag_value(employee_element, "PersonNm")
        employee_data["Employee Title"] = utils.extract_single_tag_value(employee_element, "TitleTxt", optional=True)
        employee_data["Employee Address"] = utils.extract_single_tag_value(employee_element, "AddressLine1Txt", optional=True)
        # key employee type of service tag = ???
        # key employee position tag = ???
        employee_data["Employee Compensation"] = utils.extract_single_tag_value(employee_element, "CompensationAmt", optional=True)
        # key employee total compensation (all staff) =

        records.append(employee_data)

    return records


def extract_contractor_data(dom: Document, common_data: dict) -> list[dict[str, str]]:
    # TODO: No data found... Form990PartVIISectionBGrp ???
    # Fill it contractor specific
        # Section B: Independent Contractors 
            # - name, business address, description of service, compensation (all staff)
    return []


def extract_people_data(dom: Document) -> list[dict[str, str]] | None:
    common_data = extract_common_data(dom)

    employees_from_990 = extract_employee_info_1(dom=dom, common_data=common_data)
    employees_from_990EZ = extract_employee_info_2(dom=dom, common_data=common_data)
    employees_from_990PF = extract_employee_info_3(dom=dom, common_data=common_data)

    return [*employees_from_990, *employees_from_990EZ, *employees_from_990PF]
