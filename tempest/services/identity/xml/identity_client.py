# Copyright 2012 IBM Corp.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from tempest import config
from tempest.services.compute.xml import common as xml
from tempest.services.identity.json import identity_client

CONF = config.CONF

XMLNS = "http://docs.openstack.org/identity/api/v2.0"


class IdentityClientXML(identity_client.IdentityClientJSON):
    TYPE = "xml"

    def create_role(self, name):
        """Create a role."""
        create_role = xml.Element("role", xmlns=XMLNS, name=name)
        resp, body = self.post('OS-KSADM/roles',
                               str(xml.Document(create_role)))
        return resp, self._parse_resp(body)

    def create_tenant(self, name, **kwargs):
        """
        Create a tenant
        name (required): New tenant name
        description: Description of new tenant (default is none)
        enabled <true|false>: Initial tenant status (default is true)
        """
        en = kwargs.get('enabled', 'true')
        create_tenant = xml.Element("tenant",
                                    xmlns=XMLNS,
                                    name=name,
                                    description=kwargs.get('description', ''),
                                    enabled=str(en).lower())
        resp, body = self.post('tenants', str(xml.Document(create_tenant)))
        return resp, self._parse_resp(body)

    def list_tenants(self):
        """Returns tenants."""
        resp, body = self.get('tenants')
        return resp, self._parse_resp(body)

    def update_tenant(self, tenant_id, **kwargs):
        """Updates a tenant."""
        resp, body = self.get_tenant(tenant_id)
        name = kwargs.get('name', body['name'])
        desc = kwargs.get('description', body['description'])
        en = kwargs.get('enabled', body['enabled'])
        update_tenant = xml.Element("tenant",
                                    xmlns=XMLNS,
                                    id=tenant_id,
                                    name=name,
                                    description=desc,
                                    enabled=str(en).lower())

        resp, body = self.post('tenants/%s' % tenant_id,
                               str(xml.Document(update_tenant)))
        return resp, self._parse_resp(body)

    def create_user(self, name, password, tenant_id, email, **kwargs):
        """Create a user."""
        create_user = xml.Element("user",
                                  xmlns=XMLNS,
                                  name=name,
                                  password=password,
                                  tenantId=tenant_id,
                                  email=email)
        if 'enabled' in kwargs:
            create_user.add_attr('enabled', str(kwargs['enabled']).lower())

        resp, body = self.post('users', str(xml.Document(create_user)))
        return resp, self._parse_resp(body)

    def update_user(self, user_id, **kwargs):
        """Updates a user."""
        if 'enabled' in kwargs:
            kwargs['enabled'] = str(kwargs['enabled']).lower()
        update_user = xml.Element("user", xmlns=XMLNS, **kwargs)

        resp, body = self.put('users/%s' % user_id,
                              str(xml.Document(update_user)))
        return resp, self._parse_resp(body)

    def enable_disable_user(self, user_id, enabled):
        """Enables or disables a user."""
        enable_user = xml.Element("user", enabled=str(enabled).lower())
        resp, body = self.put('users/%s/enabled' % user_id,
                              str(xml.Document(enable_user)), self.headers)
        return resp, self._parse_resp(body)

    def create_service(self, name, service_type, **kwargs):
        """Create a service."""
        OS_KSADM = "http://docs.openstack.org/identity/api/ext/OS-KSADM/v1.0"
        create_service = xml.Element("service",
                                     xmlns=OS_KSADM,
                                     name=name,
                                     type=service_type,
                                     description=kwargs.get('description'))
        resp, body = self.post('OS-KSADM/services',
                               str(xml.Document(create_service)))
        return resp, self._parse_resp(body)


class TokenClientXML(identity_client.TokenClientJSON):
    TYPE = "xml"

    def auth(self, user, password, tenant):
        passwordCreds = xml.Element("passwordCredentials",
                                    username=user,
                                    password=password)
        auth = xml.Element("auth", tenantName=tenant)
        auth.append(passwordCreds)
        resp, body = self.post(self.auth_url, body=str(xml.Document(auth)))
        return resp, body['access']
