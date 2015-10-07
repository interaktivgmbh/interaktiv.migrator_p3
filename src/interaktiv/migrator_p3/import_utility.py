# -*- coding: UTF-8 -*-
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from interaktiv.migrator_p3.interfaces import (
    IImportUtility
)

from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from zope.dottedname.resolve import resolve
try:
    from plone.app.event.dx.behaviors import IEventBasic
except:
    pass

# WTF: www.andreas-jung.com/contents/bad-dexterity-application-design
# from plone.event.interfaces import IEventAccessor

try:
    from plone import api
    from zope.intid.interfaces import IIntIds
    from z3c.relationfield.relation import RelationValue
    from plone.app.textfield.value import RichTextValue
    from plone.namedfile.file import (
        NamedBlobFile,
        NamedBlobImage
    )
    from OFS.Image import File
except:
    pass


# from Products.Five import BrowserView
# from zope.interface import implementedBy
# from z3c.form import field
# http://docs.plone.org/develop/plone/functionality/portlets.html
# http://www.martinaspeli.net/articles/an-introduction-to-plone-portlets

# CLASSES FOR CONVERT
from DateTime import DateTime
from datetime import datetime
import base64
from Products.CMFPlone.utils import safe_unicode


def get_import_utility():
    return getUtility(IImportUtility)


class ImportUtility(object):
    """ utility to provide methods for content import
    """

    non_auto_fields = [
        "parent_path",
        "portal_type",
        "id",
        "uuid",
        "local_roles",
        "workflow_history"
    ]

    different_type_name = {
        "Topic": "Collection",
        "ATImage": "Image",
        "ATFile": "File",
        "Large Plone Folder": "Folder",
        "PloneGlossary": "Glossary",
        "PloneGlossaryDefinition": "GlossaryDefinition",
    }

    mapping = {
        "leadImage": "image",
        "leadImage_caption": "image_caption",
        "startDate": "start_date",
        "endDate": "end_date",
        "eventUrl": "event_url",
        "contactName": "contact_name",
        "contactEmail": "contact_email",
        "contactPhone": "contact_phone"
    }

    mapping_fi = {
        "uber_title": "head_title"
    }

    def set_workflow_history(self, obj, data):
        if "workflow_history" not in data.keys():
            return
        wfh = data["workflow_history"]["value"]
        if not wfh:
            return
        for key in wfh.keys():
            for entry in wfh[key]:
                entry['time'] = DateTime(entry['time'])
        obj.workflow_history = wfh

    def set_local_roles(self, obj, data):
        # TODO No Local Roles ???
        if 'local_roles' not in data.keys():
            return
        local_roles = data['local_roles']["value"]
        for key in local_roles.keys():
            obj.manage_setLocalRoles(
                key,
                local_roles[key]
            )

    def set_exclude_from_nav(self, obj, data):
        if data.get('excludeFromNav', False):
            obj.exclude_from_nav = True
        else:
            obj.exclude_from_nav = False

    def set_default_view(self, obj, data):
        if not data.get("default_view", {}):
            return
        view_id = str(data["default_view"]["value"])
        if view_id == "view":
            return
        fti = obj.getTypeInfo()
        # set default view
        if view_id in fti.view_methods:
            obj.setLayout(view_id)
            return
        # set default page
        obj.setDefaultPage(view_id)

    def set_portlets(self, obj, data):
        if not data.get("portlets", {}):
            return
        for manager_name in data["portlets"]["value"].keys():
            manager = getUtility(
                IPortletManager,
                name=manager_name,
                context=obj
            )
            mapping = getMultiAdapter(
                (obj, manager),
                IPortletAssignmentMapping
            )
            for portlet_item in data["portlets"]["value"][manager_name]:
                if portlet_item["portlet_id"] not in mapping:
                    dp_identifier = portlet_item["provider_identifier"]
                    identifier_parts = dp_identifier.split(".")[:-1]
                    identifier_parts.append("Assignment")
                    try:
                        as_identifier = ".".join(identifier_parts)
#                        as_identifier = as_identifier.replace(
#                            "fi.theme",
#                            "fi.rdtheme"
#                        )
                        assignment = resolve(as_identifier)
                    except:
                        print "ERROR SETTING PORTLET: %s / %s" % (
                            data["id"]["value"],
                            data["title"]["value"]
                        )
                        return
                        # import pdb; pdb.set_trace()
                    #
                    if "hide" in portlet_item["values"].keys():
                        del portlet_item["values"]["hide"]
                    mapping[portlet_item["portlet_id"]] = assignment(
                        **portlet_item["values"]
                    )

    def set_creator_and_owner(self, obj, data):
        if 'creators' not in data.keys():
            return
        creators = data['creators']['value']
        if not creators:
            return
        if not isinstance(creators, list):
            creators = [creators]

        user = api.user.get(str(creators[0]))
        if not user:
            return
        obj.changeOwnership(user)
        obj.setCreators(tuple(creators))

    def get_references(self, value, obj):
        portal = getToolByName(obj, 'portal_url').getPortalObject()
        paths = value["paths"]
        if isinstance(paths, list):
            relations = []
            for path in paths:
                try:
                    obj = portal.restrictedTraverse(str(path))
                    if obj:
                        # create relation value
                        intid = getUtility(IIntIds).getId(obj)
                        relation = RelationValue(intid)
                        relations.append(relation)
                except:
                    continue
            return relations
        else:
            try:
                obj = portal.restrictedTraverse(str(paths))
            except:
                obj = None
            if obj:
                # create relation value
                intid = getUtility(IIntIds).getId(obj)
                relation = RelationValue(intid)
                return relation
        return ""

    def set_fields(self, obj, data):
        for key in data.keys():
            if key in self.non_auto_fields:
                continue
            # Todo Fix creators
            if key == "creators":
                continue

            value = data[key]["value"]

            if data[key]["type"] == "DateTime":
                value = DateTime(value)
                # Use Setter for Effective Date
                if key == "effectiveDate":
                    obj.setEffectiveDate(value)
                    continue
            if data[key]["type"] == "RichText":
                value = RichTextValue(
                    value,
                    'text/html',
                    'text/x-plone-outputfilters-html',
                )
            # Image Fields
            if data[key]["type"] == "Image":
                if not value['data']:
                    continue
                value = NamedBlobImage(
                    data=base64.b64decode(value['data']),
                    contentType=str(value['contentType']),
                    filename=safe_unicode(value['filename']),
                )
            # File Fields
            if data[key]["type"] == "File":
                value = NamedBlobFile(
                    data=base64.b64decode(value['data']),
                    contentType=str(value['contentType']),
                    filename=safe_unicode(value['filename']),
                )
            # ToDo References
            if data[key]["type"] == "Reference":
                value = self.get_references(data[key]["value"], obj)
            # Mapping field id
            key = self.mapping.get(key, key)
            key = self.mapping_fi.get(key, key)
            try:
                setattr(obj, key, value)
            except:
                pass

    def format_datetime(self, date):
        return datetime(
            date.year(),
            date.month(),
            date.day(),
            date.hour(),
            date.minute()
        )

    def set_event_fields(self, obj, data):
        self.set_fields(obj, data)
        #
        event = IEventBasic(obj)
        start = DateTime(data["startDate"]["value"])
        event.start = self.format_datetime(start)
        end = DateTime(data["endDate"]["value"])
        event.end = self.format_datetime(end)
        event.timezone = 'CET'

    def create_content(self, data, context):
        # Map Portal Types
        data["portal_type"]["value"] = self.different_type_name.get(
            data["portal_type"]["value"],
            data["portal_type"]["value"]
        )
        # Check if Type is available
        portal_types = getToolByName(context, "portal_types")
        types = portal_types.listContentTypes()
        if data["portal_type"]["value"] not in types:
            return

        # TODO Topic to Collection / FormGen / PloneGlossary
        #      ContentProxy
        if data["portal_type"]["value"] in [
            "FormFolder",
            "ContentProxy"
        ]:
            return

#        # ToDo PloneBoard
#        if "Ploneboard" in data["portal_type"]["value"]:
#            return

        # ToDo check and Fix Collection
        if "Criterion" in data["portal_type"]["value"]:
            return
        if "Criteria" in data["portal_type"]["value"]:
            return
        #
        if "parent_path" in data.keys():
            if "neue-inhalte" in data["parent_path"]["value"]:
                return
            if "veranstaltungen-elsass" in data["parent_path"]["value"]:
                return

        # TODO FI ALIAS Contenttype
        # TODO FI GLOSSARY Contenttype
        # TODO FI FormGen Contenttype
        if data["portal_type"]["value"] in ["Alias"]:
            return
        #
        #    # TODO Image Sizes

        portal = getToolByName(context, 'portal_url').getPortalObject()

        try:
            if "parent_path" not in data.keys():
                parent = portal
            else:
                parent = portal.restrictedTraverse(
                    str(data["parent_path"]["value"])
                )
        except:
            print "################################"
            print "ERROR GETTING PARENT: %s" % (
                str(data["parent_path"]["value"])
            )
            return

        if data["portal_type"]["value"] == "Topic":
            print "HOTTOPIC"

        if data["portal_type"]["value"] == "PloneboardComment":
            creator = data["creators"]["value"][0]
            obj = parent.addComment(
                data["title"]["value"],
                data["text"]["value"],
                creator=creator
            )
            obj.setCreationDate(DateTime(
                data["creation_date"]["value"]
            ))
            if "attachments" not in data.keys():
                return
            for at in data["attachments"]["value"]:
                at_file = File(
                    str(at["id"]),
                    safe_unicode(at["filename"]),
                    base64.b64decode(str(at["data"])),
                    str(at["contentType"])
                )
                obj.addAttachment(at_file)
            return
        else:
            if data['id']["value"] not in parent.objectIds():
                parent.invokeFactory(
                    type_name=data["portal_type"]["value"],
                    id=data['id']["value"],
                )
            obj = parent[data['id']['value']]

        if obj.portal_type == "Event":
            self.set_event_fields(obj, data)
#        elif obj.portal_type == "News Item":
#            import pdb; pdb.set_trace()
        else:
            self.set_fields(obj, data)

        #
        self.set_workflow_history(obj, data)
        self.set_local_roles(obj, data)
        self.set_exclude_from_nav(obj, data)
        self.set_default_view(obj, data)
        self.set_portlets(obj, data)
        self.set_creator_and_owner(obj, data)
        #
        obj.reindexObjectSecurity()
