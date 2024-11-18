# requirements
 Automatic requirements.txt installation

 [![Test requirements on linux, mac and windows](https://github.com/Zuzu-Typ/requirements/actions/workflows/test.yml/badge.svg)](https://github.com/Zuzu-Typ/requirements/actions/workflows/test.yml)

## Usage
In order to use `requirements` to install your dependencies from `requirements.txt`, you only have to add this repository to yours as a submodule
```Shell
git submodule add https://github.com/Zuzu-Typ/requirements
git submodule update --init --recursive
```

Then you can install all requirements from your `requirements.txt` file automatically as needed using
```Python
from requirements import requirements
```

Additionaly you can specify the filepath using:
```Python
import os
os.environ["PyPI_REQUIREMENTS_PATH"] = "/path/to/a/requirements.txt"

[ ... ]

from requirements import requirements
```

and you can disable the output of `pip` like so:
```Python
from requirements import silent, requirements
```

or alternatively:
```Python
import os
os.environ["PyPI_REQUIREMENTS_OUTPUT"] = "OFF"

[ ... ]

from requirements import requirements
```

## Example
Let's say you need the modules `Pillow`, `winput` and `PyGLM` for your project.  
You compose the following `requirements.txt` file:
```
Pillow >= 9.0.0
winput == 1.4.0
PyGLM
```

You have added this repository as a submodule to your project.
Then your main script might look something like this:

```Python
import os

# Uncomment this line to stop pip output (not advised, as the user doesn't know what's going on):
# os.environ["PyPI_REQUIREMENTS_OUTPUT"] = "OFF"

# Uncomment this line to specify a different filepath than the default relative "requirements.txt" file
# os.environ["PyPI_REQUIREMENTS_PATH"] = "/path/to/a/requirements.txt"

# The following line will install all required packages that can be found in the requirements.txt file.
# It checks if it needs to run pip first (by looking at the installed packages in site-packages)
# It raises an IOError if the requirements file could not be found, the site-packages folder was missing
# or when running as a binary executable.
from requirements import requirements

# Now the packages are available:
import winput
import glm
import PIL

[...]

```
