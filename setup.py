"""
Oauth jaccount python package configuration.

tc-imba <liuyh615@sjtu.edu.cn>
"""

from setuptools import setup

setup(
    name='oauthjaccount',
    version='0.1.0',
    packages=['oauthjaccount'],
    include_package_data=True,
    install_requires=[
        'oauthlib'
    ]
)
