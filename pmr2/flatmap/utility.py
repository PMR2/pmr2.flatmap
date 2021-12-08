import os
import json
from os.path import join, dirname, isdir
from shutil import rmtree
from subprocess import Popen
from logging import getLogger
from distutils.spawn import find_executable

import zope.component
import zope.interface

from plone.registry.interfaces import IRegistry

from pmr2.flatmap.interfaces import IMapDataMakerUtility
from pmr2.flatmap.interfaces import ISettings

logger = getLogger(__name__)
prefix = 'pmr2.flatmap.settings'


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
