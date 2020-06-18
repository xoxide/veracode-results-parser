#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='veracode-results-parser',
    version='0.1.0',
    description="A python script for Veracode results handling in a Jenkins pipeline",
    long_description=readme + '\n\n',
    author="Cory Imel",
    author_email='contact@coryimel.com',
    url='https://github.com/cory-imel/veracode-results-parser',
    packages=[
        'veracode-results-parser',
    ],
    package_dir={'veracode-results-parser':
                 'veracode-results-parser'},
    install_requires=[],
    include_package_data=True,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='veracode-results-parser',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[]  # FIXME: add dependencies of your package to this list
    test_suite='tests',
    setup_requires=[
        # dependency for `python setup.py test`
        'pytest-runner',
        # dependencies for `python setup.py build_sphinx`
        'sphinx',
        'recommonmark'
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pycodestyle',
    ],
    extras_require={
        'dev':  ['prospector[with_pyroma]', 'yapf', 'isort'],
    }
)
