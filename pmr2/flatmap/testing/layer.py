from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.testing import z2

from pmr2.app.exposure.tests import layer


class FlatmapLayer(PloneSandboxLayer):

    defaultBases = (layer.EXPOSURE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import pmr2.flatmap
        self.loadZCML(package=pmr2.flatmap)
        z2.installProduct(app, 'pmr2.flatmap')

    def setUpPloneSite(self, portal):
        """
        Apply the default pmr2.flatmap profile and ensure that the
        settings have the tmpdir applied in.
        """

        # install pmr2.flatmap
        self.applyProfile(portal, 'pmr2.flatmap:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'pmr2.flatmap')


FLATMAP_FIXTURE = FlatmapLayer()

FLATMAP_INTEGRATION_LAYER = IntegrationTesting(
    bases=(FLATMAP_FIXTURE,), name="pmr2.flatmap:integration")
