from unittest import TestCase, TestSuite, makeSuite

from zope.interface import implements
from zope.component import provideAdapter

from pmr2.app.interfaces import *
from pmr2.app.exposure.interfaces import *
from pmr2.app.exposure.content import ExposureContainer, Exposure
from pmr2.app.exposure.tests.base import ExposureDocTestCase

from pmr2.flatmap.annotator import FlatmapViewerAnnotator


class MockWorkspace:
    def absolute_url(self):
        return 'http://nohost/mw'

mock_workspace = MockWorkspace()

class MockExposureObject:
    # emulates all things Exposure
    implements(IExposureFolder, IExposureFile, IExposure)
    commit_id = '123'
    keys = ['valid']
    path = ''
    test_input = '{}'

    def __init__(self, filename):
        self.id = filename


class MockExposureSource:
    implements(IExposureSourceAdapter)

    def __init__(self, context):
        self.context = context

    def source(self):
        return self.context, mock_workspace, self.context.path


class TestFlatmapViewerAnnotator(TestCase):

    def setUp(self):
        self.context = MockExposureObject('demo_manifest.json')
        provideAdapter(MockExposureSource, (MockExposureObject,),
            IExposureSourceAdapter)

    def tearDown(self):
        pass

    def test_annotator_basic(self):
        annotator = FlatmapViewerAnnotator(self.context, None)
        # must assign the name like how this would have generated via
        # adapter.
        annotator.__name__ = 'flatmap_viewer'
        # TODO mock the API and fields
        # results = dict(annotator.generate())


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestFlatmapViewerAnnotator))
    return suite

