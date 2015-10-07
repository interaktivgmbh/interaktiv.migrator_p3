# -*- coding: UTF-8 -*-

import unittest2 as unittest
# from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from interaktiv.migrator_p3.export_utility import get_export_utility
from interaktiv.migrator_p3.testing import \
    INTERAKTIV_MIGRATOR_FUNCTIONAL_TESTING


class ExportUtilityTest(unittest.TestCase):

    layer = INTERAKTIV_MIGRATOR_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        #
        self.eu = get_export_utility()
        self.portal.invokeFactory(
            'Folder',
            id='folder',
            title='A Folder'
        )
        self.portal.folder.invokeFactory(
            'Document',
            id='page',
            title='A Page'
        )

    def test_test(self):
        print "TEST"
