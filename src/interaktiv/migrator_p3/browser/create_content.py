
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
try:
    import json
except ImportError:
    import simplejson as json

# import transaction

# OVERIDE THE SECURITY
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser


from interaktiv.migrator_p3.import_utility import get_import_utility


class CreateContentAPIView(BrowserView):

    def __call__(self):
        self.iu = get_import_utility()
        json_data = self.request.get("BODY", "")
        if not json_data:
            return
        data = json.loads(json_data)

        # SWITCH to Manager
        old_sm = getSecurityManager()
        tmp_user = UnrestrictedUser(
            old_sm.getUser().getId(),
            '', ['Manager'],
            ''
        )
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)
        # DO Stuff as Manager

        self.iu.create_content(data, self.context)

        # @TODO: Maybe add option to commit after all created
        # SWITCH Back
        setSecurityManager(old_sm)
        return ""
