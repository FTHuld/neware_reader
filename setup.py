import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='neware_reader',
    # version='0.0.1',
    author='Frederik Huld',
    # author_email=''
    description='Utilities for reading and writing neware nda files',
    long_description=long_description,
    long_description_content_type="text/text/x-rst",
    url='https://github.com/FTHuld/neware_reader',
    project_urls = {
        "Bug Tracker": "https://github.com/FTHuld/neware_reader/issues"
    },
    license='BSD-2',
    packages=['neware_reader'],
    install_requires=['numpy', 'pandas'],
)
