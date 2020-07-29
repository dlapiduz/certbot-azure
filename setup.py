import sys

from distutils.core import setup
from setuptools import find_packages

version = '0.1.0'

install_requires = [
    'acme>=0.29.0',
    'certbot>=1.1.0',
    'azure-mgmt-resource',
    'azure-mgmt-network',
    'azure-mgmt-dns>=3.0.0',
    'PyOpenSSL>=19.1.0',
    'setuptools',  # pkg_resources
    'zope.interface'
]

if sys.version_info < (2, 7):
    install_requires.append('mock<1.1.0')
else:
    install_requires.append('mock')

docs_extras = [
    'Sphinx>=1.0',  # autodoc_member_order = 'bysource', autodoc_default_flags
    'sphinx_rtd_theme',
]

setup(
    name='certbot-azure',
    version=version,
    description="Azure plugin for Certbot client",
    url='https://github.com/dlapiduz/certbot-azure',
    author="Diego Lapiduz",
    author_email='diego@lapiduz.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    keywords = ['certbot', 'azure', 'app_gateway', 'azure_dns'],
    entry_points={
        'certbot.plugins': [
            'azure-agw = certbot_azure.azure_agw:Installer',
            'dns-azure = certbot_azure.dns_azure:Authenticator',
        ],
    },
)
