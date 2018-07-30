[![Build status](https://dlapiduz.visualstudio.com/certbot-azure/_apis/build/status/certbot-azure-Python%20package-CI)](https://dlapiduz.visualstudio.com/certbot-azure/_build/latest?definitionId=5)

# Azure plugin for [Certbot](https://certbot.eff.org/) client

Use the certbot client to generate and install a certificate to be used with
an Azure App Gateway.

### Before you start

Before starting you need:

- An Azure account and the Azure CLI installed.
- Certbot installed locally.
- An Azure App Gateway deployed in your subscription.

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

### How to use it

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
--dns-azure --dns-azure-credentials mycredentials.json \
--dns-azure-resource-group REPLACE_WITH_RESOURCE_GROUP \
-i certbot-azure-ag:installer --certbot-azure-ag:installer-credentials mycredentials.json \
--certbot-azure-ag:installer-resource-group REPLACE_WITH_RESOURCE_GROUP \
--certbot-azure-ag:installer-app-gateway-name REPLACE_WITH_APP_GATEWAY_NAME
```

Follow the screen prompts and you should end up with the certificate in your
distribution. It may take a couple minutes to update.

### Automate renewal

To automate the renewal process without prompts (for example, with a monthly cron), you can add the certbot parameters `--renew-by-default --text`
