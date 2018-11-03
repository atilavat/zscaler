
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(

    name='zscaler',  # Required

    version='0.12',  # Required

    description='A python wrapper for Zscaler API. This project is not affiliated with Zscaler',  # Optional

    # This should be a valid link to your project's main homepage.
    #
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    url='https://github.com/atilavat/Zscaler/',  # Optional

    author='Alok Tilavat',  # Optional

    # This should be a valid email address corresponding to the author listed
    # above.
    #author_email='pypa-dev@googlegroups.com',  # Optional

    # Note that this is a string of words separated by whitespace, not a list.
    keywords='Zscaler API',  # Optional

    python_requires='>=3, <4',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=['requests'],  # Optional

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'zscaler=zscaler:main',
        ],
    },

)
