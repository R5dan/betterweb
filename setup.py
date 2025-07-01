from setuptools import setup, find_packages

VERSION = "0.1.0"
DESCRIPTION = "A pythonic version of React, allows for making full stack web apps"

def read(path):
    with open(path, "r") as f:
        return f.read()

setup(
        name="BetterWeb", 
        version=VERSION,
        author="R5dan",
        description=DESCRIPTION,
        long_description=read("README.md"),
        long_description_content_type="text/markdown",
        packages=find_packages(exclude="tests"),
        install_requires=[],
        extras_require={},
        keywords=['python', 'better web', 'web', "react", "state", "client"],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
            "Environment :: Web Environment"
        ],
        url="https://github.com/r5dan/betterweb"
)
