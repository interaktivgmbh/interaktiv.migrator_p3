
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from zope.interface import classProvides
from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.interfaces import IFolderish
from Products.Archetypes.interfaces.base import IBaseFolder

from Products.CMFCore.interfaces import IPropertiesTool
from zope.component import getUtility

from interaktiv.migrator_p3.export_utility import get_export_utility

try:
    import json
except ImportError:
    import simplejson as json


class SiteWalkerSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.portal = getToolByName(
            self.context,
            'portal_url'
        ).getPortalObject()

    def walk(self, folder):
        for item in folder.objectValues():
            # TODO COLLECTION
            if item.portal_type not in [
                "Topic",
            ]:
                if not hasattr(item, "Schemata"):
                    continue
                #
                yield item
                #
                is_folder = item.__provides__(IFolderish)
                is_basefolder = item.__provides__(IBaseFolder)
                if is_folder or is_basefolder:
                    for sub_item in self.walk(item):
                        yield sub_item

    def __iter__(self):
        for item in self.portal.objectValues():
            if not hasattr(item, "Schemata"):
                continue
            if item.portal_type in ["Plone Site"]:
                continue
            #
            yield item
            #
            is_folder = item.__provides__(IFolderish)
            is_basefolder = item.__provides__(IBaseFolder)
            if is_folder or is_basefolder:
                for tree_item in self.walk(item):
                    yield tree_item

############################################################################


class GetATDataSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.eu = get_export_utility()

    def __iter__(self):
        for item in self.previous:
            yield self.eu.get_item_data(item)

############################################################################


class GetATReferenceSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.eu = get_export_utility()

    def __iter__(self):
        for item in self.previous:
            yield self.eu.get_item_references(item)

############################################################################


class APICreateContentSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.every = int(options.get('every', 1000))
        self.eu = get_export_utility()

    def __iter__(self):
        count = 0

        prop_tool = getUtility(IPropertiesTool)
        properties = prop_tool.migrator_properties
        target_url = properties.target_url
        api_key = properties.api_key
        if target_url:
            for item in self.previous:
                # rebuild dict to have datatypes
                item["api_key"] = api_key
                data = self.eu.get_formated_data(item)
                # build JSON
                data = json.dumps(
                    data,
                    indent=2,
                    sort_keys=True,
                )
                # count = (count + 1) % self.every
                count += 1
                if not (count % 50):
                    print count
                self.eu.post_data_to_api(target_url, data)
                yield item
