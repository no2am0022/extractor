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
BUSINESS_NAME = "Business Name"
CITY_OR_TOWN = "City/Town"
STATE_OR_PROVINCE = "State/Province"
ZIPCODE = "Zip Code"
FORM_TYPE = "Type"
COUNTRY = "Country"
ADDRESS1 = "Address 1"  # changed from Number and Street (some provided only a PO Box)
ADDRESS2 = "Address 2"  # changed from Room/Suite (Most left this empty/see above)
PHONE = "Telephone Number"
OFFICER_NAME = "Signing officer name"
OFFICER_TITLE = "Signing officer title"
MISSION = "Mission/primary purpose"
REVENUE = "Total revenue"
EXPENSES = "Total expenses"
TRANSFER_TO_EXEMPT = "Transfer to an exempt non charitable related organization"
EMPLOYEES = "Total number of individuals employed in calendar year" # taken from portion titled TotalEmployeeCnt
VOLUNTEERS = "Total number of volunteers"
FMV_ASSETS = "fair market value of all assets"
EMPLOYEES_OVER_50K = "total number of employees receiving over $50k" # 990 PF specific
CONTRACTORS_OVER_100K = "total number of independent contractors receiving over $100k" # 990 specific
UNRELATED_BUSINESS_REVENUE = "Total unrelated business revenue" # 990 specific
DONOR_ADVISED_FUND = "did the organization maintain any donor advised fund" # 990 specific
LOCAL_CHAPTERS = "B10a: did the organziation have local chapters or affiliates" # 990 specific
 
def extract_common_data(dom: Document) -> dict[str, str]:
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

    # Get filer EIN
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
    # address2 was made optional because while some forms put in two lines of details for the address, some only had PO boxes or generally left this empty
    address2 = utils.extract_single_tag_value(us_address_element, "AddressLine2Txt", optional=True)

    data[CITY_OR_TOWN] = city_or_town
    data[ZIPCODE] = zipcode
    data[STATE_OR_PROVINCE] = state_or_province
    data[COUNTRY] = "US"  # If USAddress fails, we will need to change this but so far only US addresses were found 
    data[ADDRESS1] = address1
    data[ADDRESS2] = address2

    # get signing officer name and title
    business_group_element = utils.extract_single_tag(header_element, "BusinessOfficerGrp")

    signing_officer_name = utils.extract_single_tag_value(business_group_element, "PersonNm")         
    signing_officer_title = utils.extract_single_tag_value(business_group_element, "PersonTitleTxt")

    data[OFFICER_NAME] = signing_officer_name
    data[OFFICER_TITLE] = signing_officer_title

    return data


def extract_data_990(dom: Document) -> dict[str, str]:
    data = extract_common_data(dom)

    return_element = utils.extract_single_tag(dom, "Return")
    data_element = utils.extract_single_tag(return_element, "ReturnData")
    irs990_element = utils.extract_single_tag(data_element, "IRS990")

    # TODO extract 990 only fields
    mission = utils.extract_single_tag_value(irs990_element, "ActivityOrMissionDesc")
    expense = utils.extract_single_tag_value(irs990_element, "ExpenseAmt", optional=True)
    revenue = utils.extract_single_tag_value(irs990_element, "RevenueAmt", optional=True)
    num_volunteers = utils.extract_single_tag_value(irs990_element, "TotalVolunteersCnt", optional=True)
    num_employees = utils.extract_single_tag_value(irs990_element, "TotalEmployeeCnt", optional=True)
    contractors_receiving_over_100k = utils.extract_single_tag_value(irs990_element, "IndivRcvdGreaterThan100KCnt")
    unrelated_business_revenue = utils.extract_single_tag_value(irs990_element, "UnrelatedBusinessRevenueAmt", optional=True)
    donor_advised_fund = utils.extract_single_tag_value(irs990_element, "DonorAdvisedFundInd")
    local_chapters = utils.extract_single_tag_value(irs990_element, "LocalChaptersInd")


    data[MISSION] = mission
    data[EXPENSES] = expense
    data[REVENUE] = revenue
    data[EMPLOYEES] = num_employees
    data[VOLUNTEERS] = num_volunteers
    data[CONTRACTORS_OVER_100K] = contractors_receiving_over_100k
    data[UNRELATED_BUSINESS_REVENUE] = unrelated_business_revenue
    data[DONOR_ADVISED_FUND] = donor_advised_fund
    data[LOCAL_CHAPTERS] = local_chapters

    # field = some value
    # result[field name] = value

    return data


def extract_data_990EZ(dom: Document) -> dict[str, str]:
    data = extract_common_data(dom)

    return_element = utils.extract_single_tag(dom, "Return")
    data_element = utils.extract_single_tag(return_element, "ReturnData")
    irs990EZ_element = utils.extract_single_tag(data_element, "IRS990EZ")

    # TODO extract EZ only fields

    # 49a: did the org make any transfers to an exempt non charitable related org
        # most are mpty, some come out as "FALSE" and some as the numeral 0
            # TODO: figure out a consistent format for it
    transfer_to_exempt_element = utils.extract_single_tag_value(irs990EZ_element, "TrnsfrExmptNonChrtblRltdOrgInd", optional=True)
    # 51d: total number of independent contractors receiving over $100K

    data[TRANSFER_TO_EXEMPT] = transfer_to_exempt_element

    return data


def extract_data_990PF(dom: Document) -> dict[str, str]:     
    data = extract_common_data(dom)

    return_element = utils.extract_single_tag(dom, "Return")
    data_element = utils.extract_single_tag(return_element, "ReturnData")
    irs990PF_element = utils.extract_single_tag(data_element, "IRS990PF")
    employee_info_group_element = utils.extract_single_tag(irs990PF_element, "OfficerDirTrstKeyEmplInfoGrp")

    # TODO extract PF only fields 
    fmv_assets_element = utils.extract_single_tag_value(irs990PF_element, "FMVAssetsEOYAmt", optional=True) 
    other_employees_receiving_over_50k_element = utils.extract_single_tag_value(employee_info_group_element, "OtherEmployeePaidOver50kCnt", optional=True)

    data[FMV_ASSETS] = fmv_assets_element 
    data[EMPLOYEES_OVER_50K] = other_employees_receiving_over_50k_element

    # the only form with a beneficiaries section TBD

    return data



