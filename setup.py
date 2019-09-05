import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="intsights-taco",
    version="0.0.1",
    author="Intsights",
    author_email="Yair.Kuznitsov@intsights.com",
    description="Intsights open-source wrappers library for some AWS resources and high level management objects for distributed backend systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Intsights/taco",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
