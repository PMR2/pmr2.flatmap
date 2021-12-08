import zope.interface
from zope.schema import fieldproperty

from pmr2.app.annotation import note_factory as factory
from pmr2.app.annotation.note import ExposureFileNoteBase
from pmr2.app.annotation.note import ExposureFileEditableNoteBase
from pmr2.flatmap.interfaces import IFlatmapViewerNote
from pmr2.flatmap.interfaces import ISDSNote


class FlatmapViewerNote(ExposureFileNoteBase):
    """
    Flatmap description note.
    """

    zope.interface.implements(IFlatmapViewerNote)
    bearer_token = fieldproperty.FieldProperty(
        IFlatmapViewerNote['bearer_token'])
    flatmap_host = fieldproperty.FieldProperty(
        IFlatmapViewerNote['flatmap_host'])
    initial_response = fieldproperty.FieldProperty(
        IFlatmapViewerNote['initial_response'])
    map_id = fieldproperty.FieldProperty(
        IFlatmapViewerNote['map_id'])

FlatmapViewerNoteFactory = factory(FlatmapViewerNote, 'flatmap_viewer')


class SDSNote(ExposureFileNoteBase):
    """
    SDS Note
    """

    zope.interface.implements(ISDSNote)

SDSNoteFactory = factory(SDSNote, 'flatmap_sds_archive')
