from unittest import TestCase, TestSuite, makeSuite
import json
import requests

from zope.interface import implements
from zope.component import getUtility, provideAdapter
from plone.registry.interfaces import IRegistry

from pmr2.app.exposure.interfaces import (
    IExposureFolder, IExposureFile, IExposure, IExposureSourceAdapter)
from pmr2.app.exposure.content import ExposureContainer, Exposure
from pmr2.app.exposure.tests.base import ExposureDocTestCase

from pmr2.flatmap import annotator
from pmr2.flatmap.annotator import FlatmapViewerAnnotator
from pmr2.flatmap.interfaces import ISettings
from pmr2.flatmap.testing import layer
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

    layer = layer.FLATMAP_INTEGRATION_LAYER

    def setUp(self):
        self.context = MockExposureObject('demo_manifest.json')
        provideAdapter(MockExposureSource, (MockExposureObject,),
            IExposureSourceAdapter)

        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ISettings, prefix='pmr2.flatmap.settings')
        self.settings.flatmap_hosts = {
            u'Demo Flatmap Host': 'http://example.com:1234',
        }
        self.settings.flatmap_hosts_bearer_token = {}

    def tearDown(self):
        # restore any stubs of the requests module.
        annotator.requests = requests

    def setup_annotator_requests(self, bearer_token=''):
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
            ('bearer_token', bearer_token),
            ('flatmap_host', u'Demo Flatmap Host'),
        )
        # TODO mock the API and fields
        return fva

    def test_annotator_basic(self):
        results = dict(self.setup_annotator_requests().generate())
        # poke the dummy for test validation
        uri, a, kw = annotator.requests.history[0]
        self.assertEqual(uri, 'http://example.com:1234/make/map')
        self.assertEqual(json.loads(kw['data']), {
            "source": "http://nohost/mw/@@rawfile/123/demo_manifest.json"})
        self.assertEqual(kw['headers'], {'Content-Type': 'application/json'})

        self.assertEqual(results, {
            'flatmap_host': 'Demo Flatmap Host',
            'flatmap_host_root': 'http://example.com:1234',
            'initial_response': annotator.requests.response.text,
            'map_id': 'demo_mapid',
        })

    def test_annotator_auth_provided(self):
        self.settings.flatmap_hosts_bearer_token = {
            u'Demo Flatmap Host': 'registrystoredtoken',
        }
        # should override the host provided key set up above.
        results = dict(self.setup_annotator_requests(
            bearer_token='demotoken'
        ).generate())
        # poke the dummy for test validation
        uri, a, kw = annotator.requests.history[0]
        self.assertEqual(uri, 'http://example.com:1234/make/map')
        self.assertEqual(json.loads(kw['data']), {
            "source": "http://nohost/mw/@@rawfile/123/demo_manifest.json"})
        self.assertEqual(kw['headers'], {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer demotoken',
        })

        self.assertEqual(results, {
            'flatmap_host': 'Demo Flatmap Host',
            'flatmap_host_root': 'http://example.com:1234',
            'initial_response': annotator.requests.response.text,
            'map_id': 'demo_mapid',
        })

    def test_annotator_auth_registry(self):
        self.settings.flatmap_hosts_bearer_token = {
            u'Demo Flatmap Host': 'registrystoredtoken',
        }
        results = dict(self.setup_annotator_requests().generate())
        # poke the dummy for test validation
        uri, a, kw = annotator.requests.history[0]
        self.assertEqual(uri, 'http://example.com:1234/make/map')
        self.assertEqual(json.loads(kw['data']), {
            "source": "http://nohost/mw/@@rawfile/123/demo_manifest.json"})
        self.assertEqual(kw['headers'], {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer registrystoredtoken',
        })

        self.assertEqual(results, {
            'flatmap_host': 'Demo Flatmap Host',
            'flatmap_host_root': 'http://example.com:1234',
            'initial_response': annotator.requests.response.text,
            'map_id': 'demo_mapid',
        })

    def test_annotator_unauthorized(self):
        fva = self.setup_annotator_requests()
        annotator.requests = DummySession(json.dumps({
            "error": "unauthorized",
        }))
        with self.assertRaises(KeyError) as e:
            fva.generate()
        self.assertEqual(
            e.exception[0],
            "Flatmap server responded with an error: unauthorized",
        )

    def test_annotator_blank_response(self):
        fva = self.setup_annotator_requests()
        annotator.requests = DummySession(json.dumps({}))
        with self.assertRaises(KeyError) as e:
            fva.generate()
        self.assertEqual(
            e.exception[0],
            "No `map_id` found in response provided by flatmap server",
        )

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestFlatmapViewerAnnotator))
    return suite

