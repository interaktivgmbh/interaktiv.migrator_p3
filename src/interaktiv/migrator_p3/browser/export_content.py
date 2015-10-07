# -*- coding: utf-8 -*-
from collective.transmogrifier.transmogrifier import Transmogrifier
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from Products.CMFCore.interfaces import IPropertiesTool

from Products.Five import BrowserView


class ExportContentForm(BrowserView):

    template = ViewPageTemplateFile('templates/export_form.pt')

    def __call__(self):
        if "export" in self.request.form.keys():
            transmogrifier = Transmogrifier(self.context)
            transmogrifier(u'export_content')
            return "Data Export Ready"
        return self.template()

    def description(self):
        prop_tool = getUtility(IPropertiesTool)
        properties = prop_tool.migrator_properties
        url = properties.target_url
        return "<b>Export to (Target URL):</b> %s" % url


class ExportReferencesForm(BrowserView):

    template = ViewPageTemplateFile('templates/export_references_form.pt')

    def __call__(self):
        if "export" in self.request.form.keys():
            transmogrifier = Transmogrifier(self.context)
            transmogrifier(u'export_references')
            return "Reference Export Ready"
        return self.template()

    def description(self):
        prop_tool = getUtility(IPropertiesTool)
        properties = prop_tool.migrator_properties
        url = properties.target_url
        return "<b>Export References to (Target URL)</b>: %s" % url


class ExportContentView(BrowserView):

    def __call__(self):
        transmogrifier = Transmogrifier(self.context)
        transmogrifier(u'export_content')
