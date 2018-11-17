
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(

    name='zscaler',  # Required

    version='0.13',  # Required

    description='A python wrapper for Zscaler API. This project is not affiliated with Zscaler',  # Optional

    url='https://github.com/atilavat/Zscaler/',  

    author='Alok Tilavat', 
    #author_email='pypa-dev@googlegroups.com', 
    keywords='Zscaler Python Client API',  

    python_requires='>=3, <4',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=['requests', 'googlemaps'], 

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'zscaler = zscaler:main',
        ],
    },

)
