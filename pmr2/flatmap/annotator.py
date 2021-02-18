import json
import logging

import zope.interface
import zope.component

import requests

from pmr2.app.factory import named_factory
from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.annotation.interfaces import (
    IExposureFileAnnotator,
    IExposureFilePostEditAnnotator,
)
from pmr2.app.annotation.annotator import ExposureFileAnnotatorBase
from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from pmr2.flatmap.interfaces import (
    IFlatmapViewerNote,
    ISettings,
)

logger = logging.getLogger(__name__)


class FlatmapViewerAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(
        IExposureFileAnnotator, IExposureFilePostEditAnnotator)
    for_interface = IFlatmapViewerNote
    title = u'Flatmap Viewer'
    label = u'Flatmap Viewer'
    edited_names = ('bearer_token', 'flatmap_host',)

    def generate(self):
        data = dict(self.data)
        exposure, workspace, path = zope.component.getAdapter(self.context,
            IExposureSourceAdapter).source()
        source_url = '%s/@@%s/%s/%s' % (
            workspace.absolute_url(), 'rawfile', exposure.commit_id, path)

        r = requests.post('%s/make/map' % data['flatmap_host'],
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'source': source_url,
            }),
        )
        result = r.json()
        # TODO deal with/wipe API key
        return (
            ('flatmap_host', data['flatmap_host']),
            ('initial_response', r.text),
            ('map_id', result['map']),
        )

FlatmapViewerAnnotatorFactory = named_factory(FlatmapViewerAnnotator)
