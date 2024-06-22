from setuptools import find_packages, setup
from codecs import open
from os import path
import glob

from flask_tjfu_captcha import __version__, __author__

HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

SCRIPTS = [

]

PACKAGES = [
    'flask_tjfu_captcha'
]

REQUIRED_PACKAGES = [
    "captcha",
    "cryptocode",
    "Flask"
]

setup(
    name='flask-tjfu-captcha',
    packages=find_packages(include=PACKAGES),
    scripts=SCRIPTS,
    version=__version__,
    description='Implement CAPTCHA verification for Flask in a straightforward manner.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__author__,
    url="https://github.com/duynguyen02/flask-tjfu-captcha",
    install_requires=REQUIRED_PACKAGES,
    keywords=[
        "Python",
        "Flask"
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: OS Independent"
    ]
)
