# Update Sphinx docs

If you modify the project source code, you might like to update the technical docs (using Sphinx).
This can be done locally as follows:

```BASH
cd docs
make clean
sphinx-apidoc -o ./sphinx-docs/source ../src
make html
```
