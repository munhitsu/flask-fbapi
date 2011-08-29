#!/usr/bin/env python

from setuptools import setup

setup(
    name='Flask-FBAPI',
    version='0.1.5',
    url='http://github.com/munhitsu/flask-fbapi',
    license='BSD',
    author='Mateusz Lapsa-Malawski',
    author_email='mateusz@munhitsu.com',
    description='Facebook API for Flask (http://flask.pocoo.org) based applications',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=True,
    platforms='any',
    test_suite="nose.collector",
    #      package_dir={'': 'src'},
    install_requires=[
        'flask', 
        'redis', 
        'simplejson',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
