import setuptools
import os.path

tld_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(tld_dir, 'README.md'), encoding='utf-8') as fh:
    long_description = fh.read()


setuptools.setup(
    name='IntsightsTaco',
    version='0.0.1',
    author='Intsights',
    author_email='Yair.Kuznitsov@intsights.com',
    description='Intsights open-source library for some AWS resources and high level management objects for distributed backend systems',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Intsights/taco',
    packages=setuptools.find_packages(exclude=['ci_cd', 'tests']),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=['boto3>=1.9.130', 'botocore>=1.12.130', 'awscli'],

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/Intsights/taco/issues',
        'Source': 'https://github.com/Intsights/taco/',
    },
)
