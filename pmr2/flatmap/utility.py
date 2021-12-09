import os
import json
from os.path import exists, join, dirname, isdir
from shutil import rmtree
from subprocess import Popen
from logging import getLogger
from distutils.spawn import find_executable

import zope.component
import zope.interface

from plone.registry.interfaces import IRegistry

from pmr2.app.annotation.factory import has_note
from pmr2.app.exposure.interfaces import IExposureDownloadTool
from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.flatmap.interfaces import IMapDataMakerUtility
from pmr2.flatmap.interfaces import ISettings

logger = getLogger(__name__)
prefix = 'pmr2.flatmap.settings'


@zope.interface.implementer(IExposureDownloadTool)
class FlatmapSDSArchiveDownloadTool(object):
    """
    COMBINE Archive Download tool for a handcrafted manifest.
    """

    label = u'SDS Dataset Export'
    suffix = '.zip'
    mimetype = 'application/zip'

    def get_archive_path(self, exposure_object):
        settings = zope.component.queryUtility(IPMR2GlobalSettings)
        return join(
            settings.dirOf(exposure_object),
            'flatmap_sds_archive', 'dataset.zip'
        )

    def get_download_link(self, exposure_object):
        if not has_note(exposure_object, 'flatmap_sds_archive'):
            return False
        if not exists(self.get_archive_path(exposure_object)):
            return False
        return exposure_object.absolute_url() + '/flatmap_sds_archive_download'

    def download(self, exposure_object, request):
        with open(self.get_archive_path(exposure_object), 'rb') as fd:
            return fd.read()


@zope.interface.implementer(IMapDataMakerUtility)
class MapDataMakerUtility(object):

    def __call__(self, workspace, commit_id, path, output_target):
        registry = zope.component.getUtility(IRegistry)
        try:
            settings = registry.forInterface(ISettings, prefix=prefix)
        except KeyError:
            logger.warning(
                "settings for '%s' not found; the pmr2.flatmap may need to be "
                "reactivated", prefix,
            )
            return

        executable = find_executable(settings.flatmap_sds_datamaker)
        if executable is None:
            logger.warning(
                'unable to find the mapdatamaker binary; please '
                "verify the registry key '%s.flatmap_sds_datamaker' is set to "
                "the valid binary",
                prefix
            )
            return

        # restrict env to just the bare minimum, i.e. don't let things
        # like PYTHONPATH (if set) to interfere with the calling.
        env = {k: os.environ[k] for k in ('PATH',)}
        p = Popen([
            executable,
            workspace.absolute_url(), commit_id, path, output_target,
        ], env=env)
