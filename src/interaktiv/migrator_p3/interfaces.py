# -*- coding: UTF-8 -*-
from zope.interface import Interface
from zope import schema


class IExportUtility(Interface):
    """ utility to provide methods for Content Export
    """


class IImportUtility(Interface):
    """ utility to provide methods for Content Import
    """


class IConfiguration(Interface):
    """"""

    target_url = schema.TextLine(
        title=u"target url",
        required=False,
        description=u"",
    )

    api_key = schema.TextLine(
        title=u"api key",
        required=True,
        description=u"",
    )
