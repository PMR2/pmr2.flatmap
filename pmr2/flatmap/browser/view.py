import zope.component
from zope.publisher.interfaces import NotFound
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.exposure.browser.browser import ExposureFileViewBase


class FlatmapViewer(ExposureFileViewBase):
    """
    The flatmap viewer.
    """

    template = ViewPageTemplateFile('flatmap_viewer.pt')
