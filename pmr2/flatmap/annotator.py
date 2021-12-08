import json
import logging
from os import makedirs
from os.path import (
    exists,
    join,
    isdir,
)
from shutil import rmtree

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
from pmr2.app.exposure.interfaces import (
    IExposureSourceAdapter,
    IExposureWizard,
)

from pmr2.flatmap.interfaces import (
    IFlatmapViewerNote,
    IMapDataMakerUtility,
    ISDSNote,
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
            try:
                # attempt to strip token from wizard in a backhanded manner
                wizard = zope.component.getAdapter(exposure, IExposureWizard)
                views = dict(wizard.structure)[path]['views']
                dict(views)['flatmap_viewer'].pop('bearer_token', '')
            except Exception:
                # token wasn't declared via the wizard or failed to be
                # removed
                logger.exception(
                    "Failed to remove wizard bearer token for %r, %s",
                    exposure, path
                )
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


class SDSAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    for_interface = ISDSNote
    title = u'Flatmap SDS'
    label = u'Flatmap SDS Exporter'

    def generate(self):
        settings = zope.component.queryUtility(IPMR2GlobalSettings)
        root = settings.dirOf(self.context)
        view_root = join(root, self.__name__)
        if not isdir(root):
            makedirs(root)
        if exists(view_root):
            rmtree(view_root)
        makedirs(view_root)

        helper = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter)
        exposure, workspace, path = helper.source()
        output_target = join(view_root, 'dataset.zip')

        utility = zope.component.queryUtility(IMapDataMakerUtility)
        utility(workspace, exposure.commit_id, path, output_target)
        return ()

SDSAnnotatorFactory = named_factory(SDSAnnotator)
