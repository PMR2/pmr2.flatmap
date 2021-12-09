import zope.component
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.exposure.interfaces import IExposureDownloadTool
from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.exposure.browser.browser import ExposureFileViewBase


class FlatmapViewer(ExposureFileViewBase):
    """
    The flatmap viewer.
    """

    index = ViewPageTemplateFile('flatmap_viewer.pt')


class FlatmapSDSArchiveDownload(BrowserView):
    """
    Flatmap SDS Archive download
    """

    def __call__(self):
        tool = zope.component.getUtility(IExposureDownloadTool, name='flatmap_sds_archive')
        if not tool.get_download_link(self.context):
            raise NotFound(self.context, self.context.title_or_id())
        content = tool.download(self.context, self.request)
        self.request.response.setHeader('Content-Type', tool.mimetype)
        self.request.response.setHeader('Content-Length', len(content))
        self.request.response.setHeader('Content-Disposition',
            'attachment; filename="%s%s"' % (
                self.context.title_or_id(), tool.suffix))
        return content
