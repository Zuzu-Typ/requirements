
import sys, os, subprocess, re

from .packaging.requirements import Requirement, InvalidRequirement
from .packaging.version import parse as parse_version


__version__ = "1.0.0"

# Environment variable options

# Path to the requirements.txt file
REQUIREMENTS_FILE_PATH = os.environ.get("PyPI_REQUIREMENTS_PATH", os.path.realpath("requirements.txt"))

# Determines whether or not to print pip output to the console
OUTPUT_ENABLED = os.environ.get("PyPI_REQUIREMENTS_OUTPUT", "ON").upper() == "ON"


# Check if requirements.txt exists

if not os.path.exists(REQUIREMENTS_FILE_PATH) or not os.path.isfile(REQUIREMENTS_FILE_PATH):
    raise IOError("No requirements file was found at '{}'".format(REQUIREMENTS_FILE_PATH))


# Check if site-packages folder exists

site_packages_folder = None

for folder in sys.path:
    if folder.endswith("site-packages"):
        site_packages_folder = folder
        break

if not site_packages_folder:
    raise IOError("site-packages folder not found")


# Used to dissect the dist-info found in site-packages into packages and their installed version
SITE_PACKAGES_DIST_INFO_PATTERN = re.compile(r"^(.+)-([^-]+?)\.dist-info$")


# Load the requirements.txt file

requirements_file = open(REQUIREMENTS_FILE_PATH)
requirements_file_content = requirements_file.readlines()
requirements_file.close()

requirements = []

for requirement_string in requirements_file_content:
    try:
        requirements.append(Requirement(requirement_string.strip()))

    except InvalidRequirement:
        pass


# Compile a list of installed packages as found in site-packages

site_packages_dist_infos = tuple(map(SITE_PACKAGES_DIST_INFO_PATTERN.match, os.listdir(site_packages_folder)))

installed_packages = {}

for dist_info_match in site_packages_dist_infos:
    if dist_info_match:
        try:
            installed_packages[dist_info_match.group(1)] = parse_version(dist_info_match.group(2))
        except ValueError:
            pass


# Find out if any required package is missing

need_to_run = False

for requirement in requirements:
    if not requirement.name in installed_packages or not requirement.specifier.contains(installed_packages[requirement.name]):
        need_to_run = True
        break

# Use pip to install all required packages
if need_to_run:
    if OUTPUT_ENABLED:
        print("Some requirements were missing.\nInstalling them now...", flush=True)
        
    install_command = "{} -m pip install -r {}".format(
        sys.executable,
        REQUIREMENTS_FILE_PATH
    )

    popen = subprocess.Popen(install_command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True,
                             shell=True)

    for stdout_line in iter(popen.stdout.readline, ""):
        if OUTPUT_ENABLED: print(stdout_line, end="")

    for stdout_line in iter(popen.stderr.readline, ""):
        if OUTPUT_ENABLED: print(stdout_line, end="", file=sys.stderr)
        
    popen.stdout.close()

    popen.wait()
    
