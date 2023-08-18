# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.compat import unittest
from ansible.module_utils import basic
import ansible_collections.community.general.plugins.modules.redfish_info as module
from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args, exit_json, fail_json
from ansible_collections.community.general.tests.unit.plugins.modules.utils import get_bin_path, get_redfish_facts, get_exception_message


class TestRedfishInfo(unittest.TestCase):
    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json,
                                                 get_bin_path=get_bin_path)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def empty_return(*args, **kwargs):
        return {"ret": True}

    def mock_manager_inventory(*args, **kwargs):
        return {
            "data": {
                "FirmwareVersion": "1.0.0",
                "ManagerType": "BMC",
                "Manufacturer": "Vendor Inc.",
                "Status": {
                    "Health": "OK",
                    "State": "Enabled"
                },
                "UUID": "uuid123",
            },
            "ret": True,
        }

    def test_manager_inventory_pass(self):
        set_module_args({
            'category': 'Manager',
            'command': 'GetManagerInventory',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'baseuri': 'server-ip',
        })

        with patch.multiple(RedfishUtils,
                            create=True,
                            manager_uri="/redfish/v1/Managers/Self",
                            manager_uris=["/redfish/v1/Managers/Self"],
                            _find_managers_resource=self.empty_return,
                            get_request=self.mock_manager_inventory):
            with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                module.main()
            redfish_facts = get_redfish_facts(ansible_exit_json)
            self.assertEqual(self.mock_manager_inventory()["data"],
                             redfish_facts["manager"]["entries"][0][1])

    def test_manager_inventory_with_resource_id_pass(self):
        set_module_args({
            'category': 'Manager',
            'command': 'GetManagerInventory',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'baseuri': 'server-ip',
            'resource_id': "/redfish/v1/Managers/2"
        })

        with patch.multiple(RedfishUtils,
                            create=True,
                            manager_uri="/redfish/v1/Managers/2",
                            manager_uris=["/redfish/v1/Managers/1", "/redfish/v1/Managers/2", "/redfish/v1/Managers/3"],
                            _find_managers_resource=self.empty_return,
                            get_request=self.mock_manager_inventory):
            with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                module.main()
            redfish_facts = get_redfish_facts(ansible_exit_json)
            expected = self.mock_manager_inventory()["data"]
            expected["manager_uri"] = "/redfish/v1/Managers/2"
            actual = redfish_facts["manager"]["entries"][0]
            self.assertEqual(expected, actual)

    def mock_system_inventory(*args, **kwargs):
        return {
            "data": {
                "Status": {
                    "Health": "OK",
                    "State": "Enabled"
                },
                "PowerState": "On",
                "Manufacturer": "Vendor Inc.",
                "BiosVersion": "1.0.0",
            },
            "ret": True,
        }

    def test_systems_inventory_pass(self):
        set_module_args({
            'category': 'Systems',
            'command': 'GetSystemInventory',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'baseuri': 'server-ip',
        })

        with patch.multiple(RedfishUtils,
                            create=True,
                            systems_uri="/redfish/v1/Systems/Self",
                            systems_uris=["/redfish/v1/Systems/Self"],
                            _find_systems_resource=self.empty_return,
                            get_request=self.mock_system_inventory):
            with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                module.main()
            redfish_facts = get_redfish_facts(ansible_exit_json)
            self.assertEqual(self.mock_system_inventory()["data"],
                             redfish_facts["system"]["entries"][0][1])

    def test_systems_inventory_with_resource_id_pass(self):
        set_module_args({
            'category': 'Systems',
            'command': 'GetSystemInventory',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'baseuri': 'server-ip',
            'resource_id': "/redfish/v1/Systems/2"
        })

        with patch.multiple(RedfishUtils,
                            create=True,
                            systems_uri="/redfish/v1/Systems/2",
                            systems_uris=["/redfish/v1/Systems/1", "/redfish/v1/Systems/2", "/redfish/v1/Systems/3"],
                            _find_systems_resource=self.empty_return,
                            get_request=self.mock_system_inventory):
            with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                module.main()
            redfish_facts = get_redfish_facts(ansible_exit_json)
            expected = self.mock_system_inventory()["data"]
            expected["system_uri"] = "/redfish/v1/Systems/2"
            actual = redfish_facts["system"]["entries"][0]
            self.assertEqual(expected, actual)
