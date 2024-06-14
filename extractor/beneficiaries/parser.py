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


def extract_grantees_info(dom: Document, common_data: dict) -> list[dict[str, str]]:
    records = []
    
    grantee_elements = utils.extract_tag_instances(dom, "GrantOrContributionPdDurYrGrp")
    
    for grantee_element in grantee_elements:
        # Create a new record for this contractor and fill in common data
        grantee_data = {**common_data}
        

        grantee_name_element = utils.extract_single_tag(grantee_element, "RecipientBusinessName", optional=True)
        if not grantee_name_element:
            grantee_data["Grantee Name"] = utils.extract_single_tag_value(grantee_element,"RecipientPersonNm", optional=True)
            if not grantee_name_element:
                continue
        grantee_data["Grantee Name"] = utils.extract_single_tag_value(grantee_name_element, "BusinessNameLine1Txt")

        # Look for US address first
        grantee_address_element = utils.extract_single_tag(grantee_element, "RecipientUSAddress", optional=True)
        if not grantee_address_element:
            # Check if we have a foreign address
            grantee_address_element = utils.extract_single_tag(grantee_element, "RecipientForeignAddress", optional=True)
            if not grantee_address_element:
                # No address found!
                continue

        grantee_data["Grantee Address"] = utils.format_address(grantee_address_element)

        grantee_data["Foundation Status"] = utils.extract_single_tag_value(grantee_element, "RecipientFoundationStatusTxt", optional=True)
        grantee_data["Purpose of Grant"] = utils.extract_single_tag_value(grantee_element, "GrantOrContributionPurposeTxt")
        grantee_data["Grant Amount"] = utils.extract_single_tag_value(grantee_element, "Amt")

        # The grand total is in the parent node
        grantee_data["Total Amount"] = utils.extract_single_tag_value(grantee_element.parentNode, "TotalGrantOrContriPdDurYrAmt")

        records.append(grantee_data)

    return records


def extract_beneficiary_data(dom: Document) -> list[dict[str, str]] | None:
    common_data = extract_common_data(dom)

    beneficiaries = extract_grantees_info(dom=dom, common_data=common_data)

    return [*beneficiaries]
