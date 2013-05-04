from setuptools import setup, find_packages

from vial import VERSION

setup(
    name = 'vial',
    version = VERSION,
    author = 'Anton Bobrov',
    author_email = 'bobrov@vl.ru',
    description = 'Vim python plugin wrapper',
    long_description = open('README.rst').read(),
    zip_safe = False,
    packages = find_packages(exclude=('tests', 'tests.*')),
    include_package_data = True,
    url = 'http://github.com/baverman/vial',
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Topic :: Text Editors"
    ],
)
