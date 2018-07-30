"""Azure App Gateway Certbot installer plugin."""

from __future__ import print_function

import os
import sys
import logging
import time
import OpenSSL
import base64
try:
    from secrets import token_urlsafe
except ImportError:
    from os import urandom
    def token_urlsafe(nbytes=None):
        return urandom(nbytes)

import zope.component
import zope.interface

from certbot import interfaces
from certbot import errors

from certbot.plugins import common

from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from msrestazure.azure_exceptions import CloudError


MSDOCS = 'https://docs.microsoft.com/'
ACCT_URL = MSDOCS + 'python/azure/python-sdk-azure-authenticate?view=azure-python#mgmt-auth-file'
AZURE_CLI_URL = MSDOCS + 'cli/azure/install-azure-cli?view=azure-cli-latest'
AZURE_CLI_COMMAND = ("az ad sp create-for-rbac"
                     " --name Certbot --sdk-auth"
                     " --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP_ID"
                     " > mycredentials.json")

logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IInstaller)
@zope.interface.provider(interfaces.IPluginFactory)
class Installer(common.Plugin):

    description = "Certbot Azure Installer"

    @classmethod
    def add_parser_arguments(cls, add):
        add('credentials',
            help=(
                'Path to Azure service account JSON file. If you already have a Service ' +
                'Principal with the required permissions, you can create your own file as per ' +
                'the JSON file format at {0}. ' +
                'Otherwise, you can create a new Service Principal using the Azure CLI ' +
                '(available at {1}) by running "az login" then "{2}"' +
                'This will create file "mycredentials.json" which you should secure, then ' +
                'specify with this option or with the AZURE_AUTH_LOCATION environment variable.')
            .format(ACCT_URL, AZURE_CLI_URL, AZURE_CLI_COMMAND),
            default=None)
        add('resource-group',
            help=('Resource Group in which the DNS zone is located'),
            default=None)
        add('app-gateway-name',
            help=('Name of the application gateway'),
            default=None)

    def __init__(self, *args, **kwargs):
        super(Installer, self).__init__(*args, **kwargs)
        self.azure_client = _AzureClient(self.conf('resource-group'), self.conf('credentials'))

    def prepare(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return ("")

    def get_all_names(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def deploy_cert(self, domain, cert_path, key_path, chain_path, fullchain_path):
        """
        Upload Certificate to the app gateway
        """

        self.azure_client.update_agw(self.conf('app-gateway-name'),domain, key_path, fullchain_path)

    def enhance(self, domain, enhancement, options=None):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def supported_enhancements(self):  # pylint: disable=missing-docstring,no-self-use
        return []  # pragma: no cover

    def get_all_certs_keys(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def save(self, title=None, temporary=False):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def rollback_checkpoints(self, rollback=1):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def recovery_routine(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def view_config_changes(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def config_test(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def restart(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover



class _AzureClient(object):
    """
    Encapsulates all communication with the Azure Cloud DNS API.
    """

    def __init__(self, resource_group, account_json=None):
        self.resource_group = resource_group
        self.resource_client = get_client_from_auth_file(ResourceManagementClient,
                                                    auth_path=account_json)
        self.network_client = get_client_from_auth_file(NetworkManagementClient,
                                                    auth_path=account_json)



    def update_agw(self, agw_name, domain, key_path, fullchain_path):
        from azure.mgmt.network.models import ApplicationGatewaySslCertificate

        # Generate random password for pfx
        password = token_urlsafe(16)

        # Get app gateway from client
        agw = self.network_client.application_gateways.get(self.resource_group, agw_name)

        if "Updating" in [ssl.provisioning_state for ssl in agw.ssl_certificates]:
            raise errors.PluginError('There is a certificate in Updating state. Cowardly refusing to add a new one.')

        ssl = ApplicationGatewaySslCertificate()
        ssl.name = domain + str(int(time.time()))
        ssl.data = self._generate_pfx_from_pems(key_path, fullchain_path, password)
        ssl.password = password

        agw.ssl_certificates.append(ssl)

        try:
            self.network_client.application_gateways.create_or_update(self.resource_group,
                                                                      agw_name,
                                                                      agw)
        except CloudError as e:
            logger.warning('Encountered error updating app gateway: %s', e)
            raise errors.PluginError('Error communicating with the Azure API: {0}'.format(e))

    def _generate_pfx_from_pems(self, key_path, fullchain_path, password):
        """Generate PFX file out of PEMs in order to meet App Gateway requirements"""

        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization
        from cryptography import x509

        p12 = OpenSSL.crypto.PKCS12()

        # Load Key into PKCS12 object
        with open(key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

        key = OpenSSL.crypto.PKey.from_cryptography_key(private_key)
        p12.set_privatekey(key)

        # Load Cert into PKCS12 object
        with open(fullchain_path, "rb") as cert_file:
            crypto_cert = x509.load_pem_x509_certificate(
                cert_file.read(),
                default_backend())

        cert = OpenSSL.crypto.X509.from_cryptography(crypto_cert)
        p12.set_certificate(cert)

        # Export object
        data = p12.export(passphrase=password)

        # Return base64 encoded string
        return str(base64.b64encode(data), "utf-8")
