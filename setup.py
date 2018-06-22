import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sizesorter",
    version="0.1.0",
    author="Jonathon J. Howey",
    author_email="jjh@jonovate.com",
    description="Simple module to sort an iterable by apparel size and generate an iterable as well (...XS, S, M, L, XL...).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonovate/sizesorter",
    packages=setuptools.find_packages(),
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ),
    tests_require=["pytest"],
)
