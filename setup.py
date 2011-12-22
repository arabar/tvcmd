#! /usr/bin/env python

from setuptools import setup
import os


setup (
    name="tvcmd",
    version="0.1",
    description="Command line tool to keep track of tv shows",
    author="Juan Tascón",
    author_email="juantascon@gmail.com",
    maintainer="Juan Tascón",
    maintainer_email="juantascon@gmail.com",
    url="https://sourceforge.net/projects/tvcmd/",
    keywords=["tvcmd", "episodes", "tv", "shows", "cli"],
    
    packages=["tvcmd"],
    scripts=["script/tvcmd"],
    data_files=[("share/tvcmd", ["README", "share/tvcmd.svg"])],
    install_requires=[],
    license="GPL, Version 3.0" )