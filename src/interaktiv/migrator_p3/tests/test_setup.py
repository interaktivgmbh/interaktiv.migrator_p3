# -*- coding: utf-8 -*-
import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from interaktiv.migrator_p3.interfaces import IConfiguration

from interaktiv.migrator_p3.testing import \
    INTERAKTIV_MIGRATOR_INTEGRATION_TESTING


class TestSetup(unittest.TestCase):

    layer = INTERAKTIV_MIGRATOR_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_interaktiv_migrator_is_installed(self):
        pid = 'interaktiv.migrator_p3'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(
            pid in installed,
            'package %s appears not to have been installed' % pid
        )

    def test_registry_records_are_available(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IConfiguration, check=False)
        keys = [
            'target_url'
        ]
        for key in keys:
            self.assertTrue(hasattr(settings, key))


class TestUninstall(unittest.TestCase):

    layer = INTERAKTIV_MIGRATOR_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        self.qi_tool.uninstallProducts(products=['interaktiv.migrator_p3'])

    def test_uninstalled(self):
        self.assertFalse(
            self.qi_tool.isProductInstalled('interaktiv.migrator_p3')
        )

    def test_uninstall_removes_registry_records(self):
        registry = queryUtility(IRegistry)
        records = [_name for _name, record in registry.records.items()]
        keys = [
            'interaktiv.migrator.interfaces.IConfiguration.target_url'
        ]
        for key in keys:
            self.assertFalse(key in records, 'record not removed: %s' % key)
