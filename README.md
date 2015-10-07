==============================================================================
Interaktiv Migrator: Archetype to Dexterity
==============================================================================

Migration of Archetypes content to Dexterity.
Archetypes content Items are exported individually from an Archetypes based source site
to a Dexterity based target site.
For this all data of the Item is collected and posted to the target site in json format.
From the json data a new content item is created at the target site.

For this to work, there must be a matching portal_type on the target site.
The new content item will be created under the same path as the original item,
when the parent folder could not be found on the target site, the new item will not be created.
If the content item under the path already exists, it is updated.

References could not be set to non existing items. For setting reference fields it is recommended
using the @@export_references view for a second run, when all content is already created.



Tested on
---------

Plone3.3.5 to Plone4.3
Plone3.3.5 to Plone5
Plone4.3 to Plone5


Installation
------------

copy or clone repository to src folder and register in buildout.


Installation Plone3.3.5
-----------------------

Plone3.3.5 could only be used as target site.
Use interaktiv.migrator_p3 instead.

versions to be fixed:
    collective.transmogrifier = 1.4
    archetypes.schemaextender = 2.0.3



Configuration
-------------

Control Panel oder direct /@@migrator-controlpanel

For the source Site:

    "target url" the portal_root url of the target site

For the target Site:

    type mapping
    field mapping
    view mapping

    The Mappings are lists of key value pairs separeted by "|"


Preparation Source Site
-----------------------

In the control panel the target url must be set. The target url is the url to the portal root.


Preparation Target Site
-----------------------

Install all products and check that contenttypes and behaviours are available/set.
Only content is migrated, settings for the portal root (for example portlets) must be done additionally.
Check and adjust mappings in the migrator /@@migrator-controlpanel.


Usage transmogrifier based content walker
-----------------------------------------

On source site call /@@export_content and click button.

After Migration go to the ZMI of the target site:
under portal_workflow click "update security settings"
under portal_catalog/Advanced  perform a "clear and rebuild" of the catalog

To set references call /@@export_references and click button.



Usage code example
------------------


from interaktiv.migrator.export_utility import get_export_utility

export_utility = get_export_utility()
for brain in portal_catalog({'portal_type': 'News Item'}):
    export_utility.export_item(brain.getObject())



ToDo
----

migration of Collections
migration of uid links (resolveuid=...)
only migrates from Archetypes to Dexterity
creating new content in different parent folder

set portlet







