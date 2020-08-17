"""
Oauth jaccount python package configuration.

tc-imba <liuyh615@sjtu.edu.cn>
"""

from setuptools import setup

setup(
    name='oauth_jaccount',
    version='0.1.0',
    packages=['oauth_jaccount'],
    include_package_data=True,
    install_requires=[
        'oauthlib',
        'PyJWT'
    ]
)
