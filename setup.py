# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version__ = '0.1'

setup(
    name='raw-sql-migrate',
    version=__version__,
    maintainer_email='ts.taiye@live.com',
    description='Simple tool for managing raw sql migrations for Postgres',
    long_description=open('Readme.md').read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'psycopg2',
        'PyYAML',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.x',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
)
