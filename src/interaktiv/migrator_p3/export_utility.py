# -*- coding: UTF-8 -*-
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from interaktiv.migrator_p3.interfaces import (
    IExportUtility,
)

from Products.CMFCore.interfaces import IPropertiesTool

from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager

from zope.interface import implementedBy
from z3c.form import field
import inspect
# http://docs.plone.org/develop/plone/functionality/portlets.html
# http://www.martinaspeli.net/articles/an-introduction-to-plone-portlets

# CLASSES FOR CONVERT
# from DateTime import DateTime
from OFS.Image import Pdata
import base64
# from Products.CMFPlone.utils import safe_unicode

import urllib2
try:
    import json
except ImportError:
    import simplejson as json


def get_export_utility():
    return getUtility(IExportUtility)


class ExportUtility(object):
    """ utility to provide methods for content export
    """

    value_classes = [
        "str",
        "unicode",
        "int",
        "list",
        "tuple",
        "bool",
        "dict",
        "DateTime",
        "BaseUnit",
        "RichText"
    ]

    value_class_mapping = {
        "rights": "str"
    }

    def get_object_by_uid(self, context, uid):
        catalog = getToolByName(context, "portal_catalog")
        brains = catalog({"UID": uid})
        if len(brains) < 1:
            return None
        return brains[0].getObject()

    def get_wf_history(self, item):
        if not hasattr(item, "workflow_history"):
            return {}
        old_wfh = item.workflow_history
        wfh = dict()
        for key in old_wfh.keys():
            wfh[key] = []
            for entry in old_wfh[key]:
                entry['time'] = "%s" % entry['time']
                wfh[key].append(entry)
        return wfh

    def get_local_roles(self, item):
        return item.__ac_local_roles__

    def get_default_view(self, item):
        try:
            return item.defaultView()
        except:
            return ""

    def get_portlet_blacklists(self, item):
        blacklists = {}
        # Not for Collection Criteria
        if "Criterion" in item.portal_type:
            return blacklists
        if "Criteria" in item.portal_type:
            return blacklists

        for manager_name in ["plone.leftcolumn", "plone.rightcolumn"]:
            manager = getUtility(
                IPortletManager,
                name=manager_name,
                context=item
            )
            try:
                blacklist = getMultiAdapter(
                    (item, manager),
                    ILocalPortletAssignmentManager
                )
            except:
                print "ERROR GETTING PORTLET BLACKLIST"
                print item.portal_type
                print item.absolute_url()
                print "---------------------"
                continue
            blacklists[manager_name] = {
                'context': blacklist.getBlacklistStatus('context'),
                'group': blacklist.getBlacklistStatus('group'),
                'content_type': blacklist.getBlacklistStatus('content_type'),
            }
        return blacklists

    def get_portlets(self, item):
        portlets = {}
        # Not for Collection Criteria
        if "Criterion" in item.portal_type:
            return portlets
        if "Criteria" in item.portal_type:
            return portlets

        for manager_name in ["plone.leftcolumn", "plone.rightcolumn"]:
            manager = getUtility(
                IPortletManager,
                name=manager_name,
                context=item
            )
            try:
                mapping = getMultiAdapter(
                    (item, manager),
                    IPortletAssignmentMapping
                )
            except:
                print "ERROR GETTING PORTLET MAPPING"
                print item.portal_type
                print item.absolute_url()
                print "---------------------"
                continue
            portlet_items = []

            for portlet_item in mapping.items():
                assignment = portlet_item[1]
                data_provider = list(
                    implementedBy(assignment.__class__)
                )[0]
                portlet_fields = field.Fields(data_provider)
                #
                # values = {"title": getattr(assignment, "title", "")}
                values = {}
                for key in portlet_fields.keys():
                    values[key] = getattr(assignment, key, "")
                #
                portlet_items.append({
                    "portlet_id": portlet_item[0],
                    "provider_type": data_provider.__name__,
                    "provider_identifier": data_provider.__identifier__,
                    "values": values
                })
            portlets[manager_name] = portlet_items
        return portlets

    def get_image_data(self, image):
        image_data = image.data
        if not isinstance(image_data, str):
            image_data = image_data.data
        return {
            'value_class': "Image",
            'data': base64.b64encode(image_data),
            'contentType': image.getContentType(),
            'filename': image.getFilename()
        }

    def get_file_data(self, file):
        file_data = file.data
        if isinstance(file_data, Pdata):
            file_data = str(file_data)
        return {
            'value_class': "File",
            'data': base64.b64encode(file_data),
            'contentType': file.getContentType(),
            'filename': file.getFilename()
        }

    def get_item_data(self, item):
        data = dict()
        # Get Data From Schema
        schematas = item.Schemata()

        # if item.getId() != "arcachon":
        #     return data
        # if item.portal_type != "Box":
        #    return data

        for fieldset_id in schematas.keys():

            fieldset = schematas[fieldset_id]
            for key in fieldset.keys():
                value = getattr(item, key, None)

                if key == "creators":
                    value = item.Creator()
                    print value

                if not value:
                    try:
                        value = item[key]
                    except:
                        continue

                if inspect.ismethod(value):
                    value = value.__call__()

                value_class = value.__class__.__name__

                # Set References Later
                field = item.Schema().get(key)
                if field.type == "reference":
                    continue
                # Keys that must have a value
                value_required = ['image']
                if key in value_required:
                    if not value:
                        continue

                if value_class in self.value_classes:
                    if value_class == "DateTime":
                        value = "%s" % value
                    if value_class == "BaseUnit":
                        if value.mimetype == "text/html":
                            value_class = "RichText"
                        value = value()
                    elif field.widget.__class__.__name__ == "RichWidget":
                        value_class = "RichText"
                    if value_class.lower() == "tuple":
                        value = list(value)
                        value_class = value.__class__.__name__
                    #
                    value_class = self.value_class_mapping.get(
                        key,
                        value_class
                    )
                    data[key] = {
                        "value": value,
                        "value_class": value_class
                    }

                if value_class in ["Image", "BlobWrapper", "File"]:
                    if "image" in value.getContentType():
                        data[key] = {
                            "value": self.get_image_data(value),
                            "value_class": "Image"
                        }
                    else:
                        data[key] = {
                            "value": self.get_file_data(value),
                            "value_class": "File"
                        }

        if item.portal_type == "PloneboardComment":
            # import pdb; pdb.set_trace()
            if item.hasAttachment():
                data["attachments"] = []
                for at in item.getAttachments():
                    at_data = self.get_file_data(at)
                    at_data["id"] = at.getId()
                    data["attachments"].append(at_data)

        # import pdb; pdb.set_trace()
        #
        data['parent_path'] = "/".join(item.getPhysicalPath()[2:-1])
        data['portal_type'] = item.portal_type
        data['description'] = item.Description()
        #
        data['workflow_history'] = self.get_wf_history(item)
        data['local_roles'] = self.get_local_roles(item)
        try:
            data['excludeFromNav'] = item.getExcludeFromNav()
        except:
            data['excludeFromNav'] = False
        data['default_view'] = self.get_default_view(item)
        data['portlets'] = self.get_portlets(item)
        data['portlet_blacklists'] = self.get_portlet_blacklists(item)
        #
        return data

    def get_item_references(self, item):
        data = {
            "portal_type": item.portal_type,
            "id": item.getId(),
            "parent_path": "/".join(item.getPhysicalPath()[2:-1])
        }
        # Get Data From Schema
        schematas = item.Schemata()
        for fieldset_id in schematas.keys():
            fieldset = schematas[fieldset_id]
            for key in fieldset.keys():
                field = item.Schema().get(key)
                if field.type != "reference":
                    continue
                value = getattr(item, key, None)
                if not value:
                    try:
                        value = item[key]
                    except:
                        continue
                if not value:
                    continue

                data[key] = {
                    'value_class': "Reference",
                    'value': {'paths': []}
                }
                if isinstance(value, tuple) or isinstance(value, list):
                    for uid in value:
                        obj = self.get_object_by_uid(item, uid)
                        if not obj:
                            continue
                        data[key]['value']["paths"].append(
                            "/".join(obj.getPhysicalPath()[2:])
                        )
                else:
                    if isinstance(value, str):
                        obj = self.get_object_by_uid(item, value)
                        if obj:
                            path = "/".join(obj.getPhysicalPath()[2:])
                            data[key]['value']["paths"] = path
                    else:
                        path = "/".join(value.getPhysicalPath()[2:])
                        data[key]['value']["paths"] = path
        return data

    def get_formated_data(self, item):
        data = dict()
        for key in item.keys():
            if not item[key]:
                continue
            value = item[key]
            if isinstance(value, dict):
                if value.get("value_class", ""):
                    data[key] = {
                        "type": value['value_class'],
                        "value": value['value']
                    }
                    continue
            value_class = value.__class__.__name__
            data[key] = {
                "type": value_class,
                "value": value
            }
        return data

    def post_data_to_api(self, url, data):
        url = url + "/create_content"
        req = urllib2.Request(url, data, {"Content-type": "application/json"})
        try:
            urllib2.urlopen(req)
        except:
            pass

    def export_item(self, item, url=''):
        if not url:
            prop_tool = getUtility(IPropertiesTool)
            properties = prop_tool.migrator_properties
            url = properties.target_url
            if not url:
                return
            api_key = properties.api_key
            if not api_key:
                return
        data = self.get_item_data(item)
        data["api_key"] = api_key
        formated_data = self.get_formated_data(data)
        # build JSON
        json_data = json.dumps(
            formated_data,
            indent=2,
            sort_keys=True,
        )
        self.post_data_to_api(url, json_data)
