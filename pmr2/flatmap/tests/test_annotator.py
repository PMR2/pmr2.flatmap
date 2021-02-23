from unittest import TestCase, TestSuite, makeSuite
import json
import requests

from zope.interface import implements
from zope.component import provideAdapter

from pmr2.app.exposure.interfaces import (
    IExposureFolder, IExposureFile, IExposure, IExposureSourceAdapter)
from pmr2.app.exposure.content import ExposureContainer, Exposure
from pmr2.app.exposure.tests.base import ExposureDocTestCase

from pmr2.flatmap import annotator
from pmr2.flatmap.annotator import FlatmapViewerAnnotator
from pmr2.flatmap.testing.requests import DummySession


class MockWorkspace:
    def absolute_url(self):
        return 'http://nohost/mw'

mock_workspace = MockWorkspace()

class MockExposureObject:
    # emulates all things Exposure
    implements(IExposureFolder, IExposureFile, IExposure)
    commit_id = '123'
    keys = ['valid']
    test_input = '{}'

    def __init__(self, filename):
        self.id = filename
        self.path = filename


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
        # restore any stubs of the requests module.
        annotator.requests = requests

    def test_annotator_basic(self):
        annotator.requests = DummySession(json.dumps({
            "map": "demo_mapid",
            "process": 1234,
            "source": "http://nohost/mw/rawfile/123/demo_manifest.json",
            "status": "started",
        }))
        fva = FlatmapViewerAnnotator(self.context, None)
        # must assign the name like how this would have generated via
        # adapter.
        fva.__name__ = 'flatmap_viewer'
        fva.data = (
            ('bearer_token', ''),
            ('flatmap_host', 'http://example.com:1234'),
        )
        # TODO mock the API and fields
        results = dict(fva.generate())
        # poke the dummy for test validation
        uri, a, kw = annotator.requests.history[0]
        self.assertEqual(uri, 'http://example.com:1234/make/map')
        self.assertEqual(json.loads(kw['data']), {
            "source": "http://nohost/mw/@@rawfile/123/demo_manifest.json"})
        self.assertEqual(kw['headers'], {'Content-Type': 'application/json'})

        self.assertEqual(results, {
            'flatmap_host': 'http://example.com:1234',
            'initial_response': annotator.requests.response.text,
            'map_id': 'demo_mapid',
        })


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestFlatmapViewerAnnotator))
    return suite

