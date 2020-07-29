![Build and test](https://github.com/dlapiduz/certbot-azure/workflows/Build%20and%20test/badge.svg)

# Azure plugin for [Certbot](https://certbot.eff.org/) client

Use the certbot client to generate and install certificates in Azure.

Currently it supports authentication with Azure DNS and installation to Azure App Gateway.

### Before you start

Before starting you need:

- An Azure account and the Azure CLI installed.
- Certbot installed locally.

### Setup

The easiest way to install both the certbot client and the certbot-azure plugin is:

  ```bash
  pip install certbot-azure
  ```

  If you are in Mac OS you will need a local set up for Python and we recommend a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/).
  You might also need to install `dialog`: `brew install dialog`.

  If you are in Ubuntu you will need to install `pip` and other libraries:

  ```bash
  apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev zlib1g-dev dialog
  ```

  And then run `pip install certbot-azure`.


### Obtaining a certificate with Azure DNS authentication

To generate a certificate and install it in an Azure App Gateway first generate your credentials:

```bash
az ad sp create-for-rbac \
--name Certbot --sdk-auth \
--role "DNS Zone Contributor" \
--scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP_ID \
> mycredentials.json
```

Then generate the certificate:

```bash
certbot certonly -d REPLACE_WITH_YOUR_DOMAIN \
-a dns-azure --dns-azure-credentials mycredentials.json \
--dns-azure-resource-group <REPLACE_WITH_RESOURCE_GROUP>
```

Follow the screen prompts and you should end up with the certificate in your
distribution. It may take a couple minutes to update.


### Installing a certificate to an Azure App Gateway

To generate a certificate and install it in an Azure App Gateway first generate your credentials:

```bash
az ad sp create-for-rbac \
--name Certbot --sdk-auth \
--scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP_ID \
> mycredentials.json
```

Then generate and install the certificate (this example uses Azure DNS for authentication):

```bash
certbot -d REPLACE_WITH_YOUR_DOMAIN \
-a dns-azure --dns-azure-credentials mycredentials.json \
--dns-azure-resource-group <REPLACE_WITH_RESOURCE_GROUP> \
-i azure_agw --certbot-azure-ag:installer-credentials mycredentials.json \
--azure-agw-resource-group <REPLACE_WITH_RESOURCE_GROUP> \
--azure-agw-app-gateway-name <REPLACE_WITH_APP_GATEWAY_NAME>
```

Follow the screen prompts and you should end up with the certificate in your
distribution. It may take a couple minutes to update.

### Automate renewal

To automate the renewal process without prompts (for example, with a monthly cron), you can add the certbot parameters `--renew-by-default --text`
