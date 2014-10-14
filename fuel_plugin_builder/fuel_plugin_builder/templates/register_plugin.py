#!/usr/bin/env python

import json
import requests
import yaml

keystone = '0.0.0.0:5000'
master = '0.0.0.0:8000'


class KeystoneClient(object):
    """Simple keystone authentification client

    :param str username: is user name
    :param str password: is user password
    :param str auth_url: authentification url
    :param str tenant_name: tenant name
    """

    def __init__(self, username=None, password=None,
                 auth_url=None, tenant_name=None):
        self.auth_url = auth_url
        self.tenant_name = tenant_name
        self.username = username
        self.password = password

    @property
    def request(self):
        """Creates authentification session if required

        :returns: :class:`requests.Session` object
        """
        session = requests.Session()
        token = self.get_token()
        if token:
            session.headers.update({'X-Auth-Token': token})

        return session

    def get_token(self):
        try:
            resp = requests.post(
                self.auth_url,
                headers={'content-type': 'application/json'},
                data=json.dumps({
                    'auth': {
                        'tenantName': self.tenant_name,
                        'passwordCredentials': {
                            'username': self.username,
                            'password': self.password}}})).json()

            return (isinstance(resp, dict) and
                    resp.get('access', {}).get('token', {}).get('id'))
        except (ValueError, requests.exceptions.RequestException) as exc:
            print('Cannot authenticate in keystone: {0}'.format(exc))

        return None


keystone_client = KeystoneClient(
    username='admin',
    password='admin',
    auth_url='http://{0}/v2.0/tokens'.format(keystone),
    tenant_name='admin')


def register_plugin(plugin_name):
    with open('metadata.yaml') as m:
        data = yaml.load(m.read())
    print(data)
    resp = keystone_client.request.post(
        'http://{0}/api/plugins'.format(master),
        json.dumps(data))
    print(resp)

if __name__ == '__main__':
    import sys
    plugin_name = sys.argv[1]
    register_plugin(plugin_name)
