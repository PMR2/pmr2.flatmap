import json
import logging

import zope.interface
import zope.component
from plone.registry.interfaces import IRegistry

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
        settings = zope.component.getUtility(IRegistry).forInterface(
            ISettings, prefix='pmr2.flatmap.settings')

        data = dict(self.data)
        flatmap_host_root = settings.flatmap_hosts.get(data['flatmap_host'])
        if not flatmap_host_root:
            raise ValueError("'%s' does not resolve to a flatmap host" % (
                data['flatmap_host']))
        flatmap_host_token = settings.flatmap_hosts_bearer_token.get(
            data['flatmap_host'])

        exposure, workspace, path = zope.component.getAdapter(self.context,
            IExposureSourceAdapter).source()
        source_url = '%s/@@%s/%s/%s' % (
            workspace.absolute_url(), 'rawfile', exposure.commit_id, path)
        headers = {'Content-Type': 'application/json'}
        if data['bearer_token']:
            headers['Authorization'] = "Bearer %s" % data['bearer_token']
        elif flatmap_host_token:
            headers['Authorization'] = "Bearer %s" % flatmap_host_token

        flatmap_host_endpoint = '%s/make/map' % flatmap_host_root
        r = requests.post(flatmap_host_endpoint,
            headers=headers,
            data=json.dumps({
                'source': source_url,
            }),
        )
        result = r.json()
        if 'error' in result:
            raise KeyError(
                "Flatmap server responded with an error: %s" % result['error'])
        if 'map' not in result:
            raise KeyError(
                "No `map_id` found in response provided by flatmap server")
        # TODO deal with/wipe API key
        return (
            ('flatmap_host', data['flatmap_host']),
            ('flatmap_host_root', flatmap_host_root),
            ('initial_response', r.text),
            ('map_id', result['map']),
        )

FlatmapViewerAnnotatorFactory = named_factory(FlatmapViewerAnnotator)
