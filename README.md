# Literary

The plan for this package is:
1. Notebooks will be written inside `<PACKAGE_NAME>/` in literary project's root directory
2. Notebooks will respect relative imports and other pure-Python features to minimise the differences between the generated packages and the notebooks
3. A pure-python generated `lib/<PACKAGE_NAME>/` directory will be built before Poetry builds the final project.   
  E.g. 
    ```ini
    [tool.poetry]
    # ...
    packages = [
      { include = "<PACKAGE_NAME>", from = "lib" },
    ]
    ```
