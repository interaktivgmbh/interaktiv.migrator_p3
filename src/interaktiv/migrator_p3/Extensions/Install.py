from Products.CMFCore.utils import getToolByName


def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile(
            'profile-interaktiv.migrator_p3:uninstall'
        )
        return "Ran all uninstall steps."
