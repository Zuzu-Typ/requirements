import sys, os, subprocess, re



REQUIREMENTS_FILE_PATH = os.environ.get("PyPI_REQUIREMENTS_PATH", os.path.realpath("requirements.txt"))

OUTPUT_ENABLED = os.environ.get("PyPI_REQUIREMENTS_OUTPUT", "OFF").upper() == "ON"

VERSION_NUMBER_PATTERN = re.compile('([0-9]+!)?([0-9]+)((?:\\.[0-9]+)*)(?:(\\.\\*)|(?:((?:a|b|rc)[0-9]+)?(\\.post[0-9]+)?(\\.dev[0-9]+)?))')

REQUIREMENT_PATTERN = re.compile('^\\s*([A-z0-9.\\-_]+)\\s*(?:(>|<|!=|~=|==|<=|>=)\\s*((?:[0-9]+!)?(?:[0-9]+)(?:(?:\\.[0-9]+)*)(?:(?:\\.\\*)|(?:(?:(?:a|b|rc)[0-9]+)?(?:\\.post[0-9]+)?(?:\\.dev[0-9]+)?)))\\s*)?$', re.MULTILINE)

ALPHA = 0
BETA = 1
RELEASE_CANDIDATE = 2


class Version:
    def __init__(self, version_string):
        match_ = VERSION_NUMBER_PATTERN.fullmatch(version_string)

        if not match_:
            raise ValueError("Invalid version specifier")

        epoch, major, minors, wildcard, pre, post, dev = match_.groups()

        self.epoch = int(epoch.rstrip("!")) if epoch else 0
        self.major = int(major)
        self.minors = tuple(map(int, minors.split(".")[1:])) if minors else None
        self.wildcard = bool(wildcard)
        
        if pre:
            self.pre_type = ALPHA if pre[0] == "a" else BETA if pre[0] == "b" else RELEASE_CANDIDATE
            self.pre = int(pre.lstrip("abrc"))
        else:
            self.pre_type = self.pre = None
            
        self.post = int(post[len(".post"):]) if post else None
        self.dev = int(dev[len(".dev"):]) if dev else None

        self.version_string = version_string

    def copy(self):
        return Version(self.version_string)

    def __gt__(self, other):        
        if self.epoch != other.epoch:
            if self.epoch > other.epoch:
                return True
            
            return False

        if self.major != other.major:
            return self.major > other.major

        if self.minors and not other.minors and any(self.minors) or self.minors and other.minors and any(self.minors) and not any(other.minors):
            return True

        if other.minors and not self.minors and any(other.minors) or other.minors and self.minors and any(other.minors) and not any(self.minors):
            return False

        if self.minors and other.minors:
            max_len = max(len(self.minors), len(other.minors))
            
            self_minors = list(self.minors)   + [0] * (max_len - len(self.minors))
            other_minors = list(other.minors) + [0] * (max_len - len(other.minors))

            for i in range(max_len):
                self_minor = self_minors[i]
                other_minor = other_minors[i]

                if self_minor > other_minor:
                    return True

                if self_minor < other_minor:
                    return False

        if not self.pre is None and other.pre is None:
            return False

        if self.pre is None and not other.pre is None:
            return True

        if not self.pre is None and not other.pre is None:
            if self.pre_type > other.pre_type:
                return True

            if self.pre_type < other.pre_type:
                return False

            if self.pre > other.pre:
                return True

            if self.pre < other.pre:
                return False

        if not self.post is None and other.post is None:
            return True

        if self.post is None and not other.post is None:
            return False

        if not self.post is None and not other.post is None:
            if self.post > other.post:
                return True

            if self.post < other.post:
                return False

        if not self.dev is None and other.dev is None:
            return False

        if self.dev is None and not other.dev is None:
            return True

        if not self.dev is None and not other.dev is None:
            return self.dev > other.dev

        return False

    def __eq__(self, other):
        if self.epoch == other.epoch and \
           self.major == other.major and \
           self.pre_type == other.pre_type and \
           self.pre == other.pre and \
           self.post == other.post and \
           self.dev == other.dev:
            if self.minors and not other.minors and any(self.minors) or self.minors and other.minors and any(self.minors) and not any(other.minors):
                return False

            if other.minors and not self.minors and any(other.minors) or other.minors and self.minors and any(other.minors) and not any(self.minors):
                return False

            if self.minors and other.minors:
                max_len = max(len(self.minors), len(other.minors))
                
                self_minors = list(self.minors)   + [0] * (max_len - len(self.minors))
                other_minors = list(other.minors) + [0] * (max_len - len(other.minors))

                for i in range(max_len):
                    self_minor = self_minors[i]
                    other_minor = other_minors[i]

                    if self_minor != other_minor:
                        return False

            return True

        if self.epoch == other.epoch and \
           self.major == other.major and \
           (self.wildcard or other.wildcard):

            if self.minors and not other.minors:
                return other.wildcard

            if not self.minors and other.minors:
                return self.wildcard

            if not self.minors and not other.minors:
                return True
            
            if self.minors and other.minors:
                max_len = max(len(self.minors), len(other.minors))
                
                self_minors = (list(self.minors)   + [0] * (max_len - len(self.minors))) if not self.wildcard else (list(self.minors)   + [-1] * (max_len - len(self.minors)))
                other_minors = (list(other.minors) + [0] * (max_len - len(other.minors))) if not other.wildcard else (list(other.minors)+ [-1] * (max_len - len(other.minors))) 

                for i in range(max_len):
                    self_minor = self_minors[i]
                    other_minor = other_minors[i]
                    
                    if self_minor != other_minor and self_minor >= 0 and other_minor >= 0:
                        return False

                return True

        return False
                

    def __ne__(self, other):
        return not self == other

    def __ge__(self, other):
        return self == other or self > other

    def __lt__(self, other):
        return not self >= other

    def __le__(self, other):
        return not self > other

    def compatible_with(self, other):
        if self >= other:
            other_copy = other.copy()

            other_copy.wildcard = True

            if not other_copy.minors:
                return self == other_copy

            other_copy_minors = list(other_copy.minors)
            other_copy_minors.pop()
            other_copy.minors = tuple(other_copy_minors)

            return self == other_copy

if not os.path.exists(REQUIREMENTS_FILE_PATH) or not os.path.isfile(REQUIREMENTS_FILE_PATH):
    raise IOError("No requirements file was found at '{}'".format(REQUIREMENTS_FILE_PATH))


requirements_file = open(REQUIREMENTS_FILE_PATH)

requirements_file_content = requirements_file.read()

requirements_file.close()




requirements = REQUIREMENT_PATTERN.findall(requirements_file_content)


site_packages_folder = None


for folder in sys.path:
    if folder.endswith("site-packages"):
        site_packages_folder = folder
        break


if not site_packages_folder:
    raise IOError("site-packages folder not found")


site_packages_dist_infos = tuple(filter(lambda x: x.endswith(".dist-info"), os.listdir(site_packages_folder)))

installed_packages = {}

for dist_info in site_packages_dist_infos:
    dist_info = dist_info[:-len(".dist-info")]
    dash_pos = dist_info.rindex("-")
    version = dist_info[dash_pos + 1 : ]
    package_name = dist_info[:dash_pos]
    
    installed_packages[package_name] = Version(version)

need_to_run = False

for package_name, operator, version_string in requirements:
    if not package_name in installed_packages:
        need_to_run = True
        break

    version = Version(version_string)

    if operator == "==" and not installed_packages[package_name] == version:
        need_to_run = True
        break

    if operator == "!=" and not installed_packages[package_name] != version:
        need_to_run = True
        break

    if operator == ">=" and not installed_packages[package_name] >= version:
        need_to_run = True
        break

    if operator == "<=" and not installed_packages[package_name] <= version:
        need_to_run = True
        break

    if operator == ">" and not installed_packages[package_name] > version:
        need_to_run = True
        break

    if operator == "<" and not installed_packages[package_name] < version:
        need_to_run = True
        break

    if operator == "~=" and not installed_packages[package_name].compatible_with(version):
        need_to_run = True
        break

if need_to_run:
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
    
