"""Tests for certbot_dns_azure.dns_azure."""

import os
import unittest

import mock
import json

from certbot import errors
from certbot.plugins import dns_test_common_lexicon
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util
from requests import Response

from msrestazure.azure_exceptions import CloudError
from azure.mgmt.network.models import ApplicationGateway
from azure.mgmt.network.models import ApplicationGatewaySslCertificate


RESOURCE_GROUP = 'test-test-1'

class AzureClientTest(test_util.TempDirTestCase):
    zone = "foo.com"
    record_name = "bar"
    record_content = "baz"
    record_ttl = 42

    def _getCloudError(self):
        response = Response()
        response.status_code = 500
        return CloudError(response)

    def _generate_dummy_agw(self):
        agw = ApplicationGateway()
        agw.name = "Test"
        agw.ssl_certificates = []
        return agw

    def setUp(self):
        from certbot_azure.installer import _AzureClient
        super(AzureClientTest, self).setUp()

        config_path = AzureClientConfigDummy.build_config(self.tempdir)

        self.azure_client = _AzureClient(RESOURCE_GROUP, config_path)

        self.resource_client = mock.MagicMock()
        self.network_client = mock.MagicMock()
        self.azure_client.resource_client = self.resource_client
        self.azure_client.network_client = self.network_client
        # pylint: disable=protected-access
        self.azure_client._generate_pfx_from_pems = mock.MagicMock()

    def test_update_agw(self):
        agw = self._generate_dummy_agw()
        # pylint: disable=protected-access
        self.network_client.application_gateways.get.return_value = agw

        self.azure_client.update_agw(agw.name,
                                     "test_domain.com",
                                     "test_key_path",
                                     "test_cert_path")

        self.network_client.application_gateways.create_or_update.assert_called_with(
            self.azure_client.resource_group,
            agw.name,
            mock.ANY)

        updated_agw = self.network_client.application_gateways.create_or_update.call_args[0][2]

        self.assertEqual(len(updated_agw.ssl_certificates), 1)

    def test_update_agw_error(self):
        agw = self._generate_dummy_agw()
        # pylint: disable=protected-access
        self.network_client.application_gateways.get.return_value = agw
        self.network_client.application_gateways.create_or_update.side_effect = self._getCloudError()

        with self.assertRaises(errors.PluginError):
            self.azure_client.update_agw(agw.name,
                                        "test_domain.com",
                                        "test_key_path",
                                        "test_cert_path")

    def test_update_agw_error_if_pending(self):
        agw = self._generate_dummy_agw()
        ssl = ApplicationGatewaySslCertificate()
        ssl.provisioning_state = 'Updating'
        agw.ssl_certificates = [ssl]
        # pylint: disable=protected-access
        self.network_client.application_gateways.get.return_value = agw

        with self.assertRaises(errors.PluginError):
            self.azure_client.update_agw(agw.name,
                                        "test_domain.com",
                                        "test_key_path",
                                        "test_cert_path")


class AzureClientConfigDummy(object):
    """Helper class to create dummy Azure configuration"""

    @classmethod
    def build_config(cls, tempdir):
        """Helper method to create dummy Azure configuration"""

        config_path = os.path.join(tempdir, 'azurecreds.json')
        with open(config_path, 'w') as outfile:
            json.dump({
                "clientId": "uuid",
                "clientSecret": "uuid",
                "subscriptionId": "uuid",
                "tenantId": "uuid",
                "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
                "resourceManagerEndpointUrl": "https://management.azure.com/",
                "activeDirectoryGraphResourceId": "https://graph.windows.net/",
                "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
                "galleryEndpointUrl": "https://gallery.azure.com/",
                "managementEndpointUrl": "https://management.core.windows.net/"
            }, outfile)

        return config_path

if __name__ == "__main__":
    unittest.main()  # pragma: no cover

