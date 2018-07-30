import sys

from distutils.core import setup
from setuptools import find_packages

version = '0.0.1'

install_requires = [
    'acme>=0.26.1',
    'certbot>=0.26.0',
    'azure-mgmt-resource',
    'azure-mgmt-network',
    'PyOpenSSL>=17.1.0',
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
    description="Azure Installer plugin for Certbot client",
    url='https://github.com/dlapiduz/certbot-azure-ag',
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
    keywords = ['certbot', 'azure', 'app_gateway'],
    entry_points={
        'certbot.plugins': [
            'installer = certbot_azure.installer:Installer',
        ],
    },
)
