# trac-subtickets-plugin
A sub-ticket support plugin for trac

# Release

1. Comment out the following in `setup.cfg` and commit:
    ```
    [egg_info]
    tag_build = dev
    ```
1. Tag the release:
    ```
    git tag <version>
    git push --tags
    ```
1. Create the release and upload to [PyPI](https://pypi.org/project/TracSubTickets/):

    ```
    rm -rf dist
    python setup.py release
    twine upload dist/*
    ```
