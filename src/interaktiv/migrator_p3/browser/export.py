# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Five import BrowserView

from interaktiv.migrator_p3.export_utility import get_export_utility


class ExportContextView(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        self.eu = get_export_utility()
        self.eu.export_item(context)
        return "exported: %s" % context.Title()
