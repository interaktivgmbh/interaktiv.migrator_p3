
from zope.formlib import form
from zope.interface import implements
from zope.component import adapts, getUtility

from plone.app.controlpanel.form import ControlPanelForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from interaktiv.migrator_p3.interfaces import IConfiguration

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import IPropertiesTool


class ConfigurationControlPanelAdapter(SchemaAdapterBase):
    """ Control Panel adapter """

    adapts(IPloneSiteRoot)
    implements(IConfiguration)

    def __init__(self, context):
        super(ConfigurationControlPanelAdapter, self).__init__(context)
        prop_tool = getUtility(IPropertiesTool)
        self.properties = prop_tool.migrator_properties

    def get_target_url(self):
        return self.properties.target_url

    def set_target_url(self, url):
        self.properties.target_url = url

    target_url = property(get_target_url, set_target_url)

    def get_api_key(self):
        return self.properties.api_key

    def set_api_key(self, key):
        self.properties.api_key = key

    api_key = property(get_api_key, set_api_key)


class ConfigurationForm(ControlPanelForm):
    implements(IConfiguration)

    form_fields = form.Fields(IConfiguration)
    label = u"Migrator Configuration"
    description = ""

    template = ViewPageTemplateFile('controlpanel.pt')
