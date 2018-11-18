
from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Pyno',
    # TODO: "pyno" already exists on PyPI, maybe rename?

    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.2.0',  # Required
    description='Python-based data-flow visual programming',
    long_description=long_description,
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/honix/Pyno',
    author='Fyodor Shchukin',
    author_email='ted888@ya.ru',

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().

    # FIXME: this excludes the examples
    packages=find_packages(exclude=['docs', 'tests']),  # Required
    install_requires=['pyglet', 'pyperclip'],
    extras_require={
        'test': ['pytest', 'coverage'],
    },
    package_data={
        'pyno': ['imgs/*.png', 'examples/*.pn'],

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    #
    #TODO: do these following points
    package_data={  # Optional
        'pyno': ['imgs/*.png'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    #
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],  # Optional

    entry_points={
        'console_scripts': [
            'pyno=pyno.window:app_run',
        ],
    },
)
