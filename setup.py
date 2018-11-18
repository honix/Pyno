from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Keep version string only in one place to avoid duplication
# Read the string from code without importing to avoid problems at setup
with open(path.join('pyno', '__init__.py')) as init:
    for l in init.readlines():
        if l.startswith('__version__'):
            version = l.split('=')[1].strip(" '\r\n")

setup(
    name='Pyno',
    # TODO: "pyno" already exists on PyPI, maybe rename?
    version=version,
    description='Python-based data-flow visual programming',
    long_description=long_description,
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/honix/Pyno',
    author='Fyodor Shchukin',
    author_email='ted888@ya.ru',
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
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
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=['pyglet', 'pyperclip'],
    extras_require={
        'test': ['pytest'],
    },
    package_data={
        'pyno': ['imgs/*.png', 'examples/*.pn'],
    },
    entry_points={
        'console_scripts': [
            'pyno=pyno.window:app_run',
        ],
    },
)
