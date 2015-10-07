# -*- coding: utf-8 -*-
from collective.transmogrifier.transmogrifier import Transmogrifier
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from Products.CMFCore.utils import getToolByName

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
#        registry = queryUtility(IRegistry)
#        settings = registry.forInterface(IConfiguration, check=False)
#        return "<b>Target URL</b>: %s" % settings.target_url
        return "settings info"


class ExportReferencesForm(BrowserView):

    def __call__(self):
        if "export" in self.request.form.keys():
            transmogrifier = Transmogrifier(self.context)
            transmogrifier(u'export_references')
            return "Data Export Ready"
        return self.template()

    def description(self):
#        registry = queryUtility(IRegistry)
#        settings = registry.forInterface(IConfiguration, check=False)
#        return "<b>Target URL</b>: %s" % settings.target_url
        return "settings info"


class ExportContentView(BrowserView):

    def __call__(self):
        transmogrifier = Transmogrifier(self.context)
        transmogrifier(u'export_content')
