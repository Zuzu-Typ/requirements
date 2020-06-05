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