#!/usr/bin/env python

from setuptools import setup
import sys

from bos_incidents import __VERSION__

assert sys.version_info[0] == 3, "We require Python > 3"

setup(
    name='bos-incidents',
    version=__VERSION__,
    description=(
        'Private module for BOS incident storage'
    ),
    long_description=open('README.md').read(),
    download_url='https://github.com/pbsa/bos-incidents/tarball/' + __VERSION__,
    author='Blockchain BV',
    author_email='info@blockchainbv.com',
    maintainer='Stefan Schießl',
    maintainer_email='Stefan.Schiessl@BlockchainProjectsBV.com',
    url='http://pbsa.info',
    keywords=['peerplays', 'bos'],
    packages=[
        "bos_incidents",
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    install_requires=open('requirements.txt').readlines(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
)
