# Copyright (C) 2020 Samuel Baker

DESCRIPTION = "Making modular figures with blender"
LONG_DESCRIPTION = """
# pyBlendFigures

Making modular figures with blender

"""
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"

DISTNAME = 'pyBlendFigures'
MAINTAINER = 'Samuel Baker'
MAINTAINER_EMAIL = 'samuelbaker.researcher@gmail.com'
LICENSE = 'MIT'
DOWNLOAD_URL = "https://github.com/sbaker-dev/pyBlendFigures"
VERSION = "0.04.0"
PYTHON_REQUIRES = ">=3.7"

INSTALL_REQUIRES = [
    'miscSupports', 'csvObject', 'numpy', 'imageObjects', "shapeObject", 'blendSupports', 'shapely', 'seaborn']

CLASSIFIERS = [
    'Programming Language :: Python :: 3.7',
    'License :: OSI Approved :: MIT License',
]

if __name__ == "__main__":

    from setuptools import setup, find_packages

    import sys

    if sys.version_info[:2] < (3, 7):
        raise RuntimeError("pyBlendFigures requires python >= 3.7.")

    setup(
        name=DISTNAME,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
        license=LICENSE,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        python_requires=PYTHON_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        include_package_data=True,
        packages=find_packages(),
        classifiers=CLASSIFIERS
    )
