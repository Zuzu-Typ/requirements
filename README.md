# requirements
 Automatic requirements.txt installation

## Usage
In order to use `requirements` to install your dependencies from `requirements.txt`, you only have to 
```Python
import requirements
```

Additionaly you can specify the filepath using
```Python
import os
os.environ["PyPI_REQUIREMENTS_PATH"] = "/path/to/a/requirements.txt"
```

and you can allow `requirements` to output messages from pip, like so:
```Python
import os
os.environ["PyPI_REQUIREMENTS_OUTPUT"] = "ON"
```

These lines must preceed the `import requirements` line though.

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

# Let the user know what's going on:
os.environ["PyPI_REQUIREMENTS_OUTPUT"] = "ON"

# The following line will install all required packages that can be found in the requirements.txt file.
# It checks if it needs to run pip first (by looking at the installed packages in site-packages)
# It raises an OSError if the file could not be found or when running as a binary executable.
from requirements import requirements

# Now the packages are available:
import winput
import glm
import PIL

[...]

```
