# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version__ = '0.1'

setup(
    name='raw-sql-migrate',
    version=__version__,
    maintainer_email='ts.taiye@live.com',
    description='Simple tool for managing raw sql migrations.',
    long_description=open('Readme.md').read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'psycopg2',
        'PyYAML',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.x',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
