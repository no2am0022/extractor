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
PHONE = "Telephone Number"
PREP_FIRM_NAME = "Firm name/Preparer name" # for accountant (TODO double check which info this pulls)
PREP_FIRM_ADDRESS = "Firm Address"
PREP_FIRM_EIN = "Firm EIN"
PREP_FIRM_CITY = "Firm City"
PREP_FIRM_STATE = "Firm Country/State"
PREP_FIRM_ZIPCODE = "Firm Zip Code"
BOOKS_NAME = "the books are in care of: Name" # 990 PF specifc
BOOKS_PHONE = "the books are in care of: Telephone" # 990 PF specifc
BOOKS_ADDRESS = "the books are in care of: Address" # 990 PF specifc
BOOKS_ZIPCODE = "the books are in care of: Zip Code" # 990 PF specifc


def extract_common_data(dom: Document) -> dict[str, str] | None:
    data = {}

    return_element = utils.extract_single_tag(dom, "Return")
    header_element = utils.extract_single_tag(return_element, "ReturnHeader")

    # Get the filing year
    tax_period_begin_text = utils.extract_single_tag_value(header_element, "TaxPeriodBeginDt")
    tax_period_begin: date = datetime.strptime(tax_period_begin_text, "%Y-%m-%d")
    data[FILING_YEAR] = tax_period_begin.year

    # get file type
    form_type = utils.extract_single_tag_value(header_element, "ReturnTypeCd")
    data[FORM_TYPE] = form_type

    filer_element = utils.extract_single_tag(header_element, "Filer")

    # Get filer EIN and phone number
    charity_ein = utils.extract_single_tag_value(filer_element, "EIN")
    phonenumber = utils.extract_single_tag_value(filer_element, "PhoneNum", optional=True)
    data[CHARITY_EIN] = charity_ein
    data[PHONE] = phonenumber

    # Get filer business name
    business_name_element = utils.extract_single_tag(filer_element, "BusinessName")
    business_name = utils.extract_single_tag_value(business_name_element, "BusinessNameLine1Txt")
    data[BUSINESS_NAME] = business_name

    # find address section and step into it
    us_address_element = utils.extract_single_tag(filer_element, "USAddress")

    # find the filer city/town
    city_or_town = utils.extract_single_tag_value(us_address_element, "CityNm")
    # find the filer zipcode
    zipcode = utils.extract_single_tag_value(us_address_element, "ZIPCd")
    # find the filer state/province
    state_or_province = utils.extract_single_tag_value(us_address_element, "StateAbbreviationCd")
    address1 = utils.extract_single_tag_value(us_address_element, "AddressLine1Txt")
    
    data[CITY_OR_TOWN] = city_or_town
    data[ZIPCODE] = zipcode
    data[STATE_OR_PROVINCE] = state_or_province
    data[COUNTRY] = "US"  # If USAddress fails, we will need to change this but so far only US addresses were found 
    data[ADDRESS1] = address1
    
    # getting accounting firm specific information
    preparer_firm_element = utils.extract_single_tag(header_element, "PreparerFirmGrp", optional=True)
    if preparer_firm_element is None:
        return None
    
    preparer_firm_name_element = utils.extract_single_tag(preparer_firm_element, "PreparerFirmName")
    preparer_firm_address_element = utils.extract_single_tag(preparer_firm_element, "PreparerUSAddress")

    preparer_firm_ein = utils.extract_single_tag_value(preparer_firm_element, "PreparerFirmEIN", optional=True)
    preparer_firm_name = utils.extract_single_tag_value(preparer_firm_name_element, "BusinessNameLine1Txt")
    preparer_firm_address = utils.extract_single_tag_value(preparer_firm_address_element, "AddressLine1Txt")
    prepare_firm_city = utils.extract_single_tag_value(preparer_firm_address_element, "CityNm")
    prepare_firm_state = utils.extract_single_tag_value(preparer_firm_address_element, "StateAbbreviationCd")
    prepare_firm_zipcode = utils.extract_single_tag_value(preparer_firm_address_element, "ZIPCd")

    data[PREP_FIRM_EIN] = preparer_firm_ein
    data[PREP_FIRM_NAME] = preparer_firm_name
    data[PREP_FIRM_ADDRESS] = preparer_firm_address
    data[PREP_FIRM_CITY] = prepare_firm_city
    data[PREP_FIRM_STATE] = prepare_firm_state
    data[PREP_FIRM_ZIPCODE] = prepare_firm_zipcode

    return data


def extract_data_990(dom: Document) -> dict[str, str] | None:
    data = extract_common_data(dom)
    return data


def extract_data_990EZ(dom: Document) -> dict[str, str] | None:
    data = extract_common_data(dom)
    return data


def extract_data_990PF(dom: Document) -> dict[str, str] | None:     
    data = extract_common_data(dom)

    return_element = utils.extract_single_tag(dom, "Return")
    data_element = utils.extract_single_tag(return_element, "ReturnData")
    irs990PF_element = utils.extract_single_tag(data_element, "IRS990PF")
    books_name_element = utils.extract_single_tag(irs990PF_element, "PersonsWithBooksName", optional=True)
    if books_name_element is None:
        return None
    
    books_location_element = utils.extract_single_tag(irs990PF_element, "LocationOfBooksUSAddress")

    books_name = utils.extract_single_tag_value(books_name_element, "BusinessNameLine1Txt")
    books_phone = utils.extract_single_tag_value(irs990PF_element, "PhoneNum")
    books_address = utils.extract_single_tag_value(books_location_element, "AddressLine1Txt") # add city and state?
    books_zipcode = utils.extract_single_tag_value(books_location_element, "ZIPCd")

    data[BOOKS_NAME] = books_name
    data[BOOKS_PHONE] = books_phone
    data[BOOKS_ADDRESS] = books_address
    data[BOOKS_ZIPCODE] = books_zipcode

    return data
