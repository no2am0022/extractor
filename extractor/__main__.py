import pathlib

from extractor.organizations import main as organizations
from extractor.accountants import main as accountants
from extractor.staff import main as staff
from extractor.beneficiaries import main as beneficiaries

base_path = pathlib.Path("./data")
output_path = pathlib.Path("./output")

# organizations.parse(base_path=base_path, output_file=output_path.joinpath("organizations.csv"))
# accountants.parse(base_path=base_path, output_file=output_path.joinpath("accountants.csv"))
# staff.parse(base_path=base_path, output_file=output_path.joinpath("staff.csv"))
beneficiaries.parse(base_path=base_path, output_file=output_path.joinpath("beneficiaries.csv"))

