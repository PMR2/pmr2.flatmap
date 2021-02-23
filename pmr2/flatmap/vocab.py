import zope.interface
import zope.component

from zope.schema.interfaces import IVocabulary, IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.registry.interfaces import IRegistry

from pmr2.flatmap.interfaces import ISettings

prefix = 'pmr2.flatmap.settings'


class FlatmapHostsVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        registry = zope.component.getUtility(IRegistry)
        try:
            settings = registry.forInterface(ISettings, prefix=prefix)
        except KeyError:
            return

        super(FlatmapHostsVocab, self).__init__([
            SimpleTerm(key, value, title=u'%s (%s)' % (key, value))
            for key, value in sorted(settings.flatmap_hosts.items())
        ])
