import zope.interface
import zope.schema

from pmr2.app.workspace.schema import StorageFileChoice


class ISettings(zope.interface.Interface):
    """
    Settings to be registered to the configuration registry.
    """

    flatmap_hosts = zope.schema.Dict(
        title=u'Flatmap Hosts',
        description=u'Configure entries for selectable flatmap hosts; '
                     'key is the name, value is the host',
        key_type=zope.schema.TextLine(
            title=u"Flatmap Server Name",
        ),
        value_type=zope.schema.ASCIILine(
            title=u"Host (e.g. http://127.0.0.1:8000; ASCII only)",
        ),
        default={},
        required=False,
    )

    flatmap_hosts_bearer_token = zope.schema.Dict(
        title=u"Flatmap Hosts' Bearer Token",
        description=u'Configure the bearer token to use with the named host; '
                     'key is the name of host, value is the token',
        key_type=zope.schema.TextLine(
            title=u"Flatmap Server Name",
        ),
        value_type=zope.schema.ASCIILine(
            title=u"Bear Token (e.g. secretbearertoken; ASCII only)",
        ),
        default={},
        required=False,
    )

    flatmap_sds_datamaker = zope.schema.TextLine(
        title=u'Flatmap SDS datamaker',
        description=u'The path to the mapdatamaker binary.',
        default=u'mapdatamaker',
        required=False,
    )


class IFlatmapViewerNote(zope.interface.Interface):
    """
    Flatmap viewer note.
    """

    # Currently, the base file will be the manifest.json, so this field
    # is not required for the moment.
    #
    # description_json = StorageFileChoice(
    #     title=u'Flatmap Description',
    #     description=u'The JSON file to be associated with the selected '
    #                  'flatmap PDF file for conversion process for the '
    #                  'viewer.',
    #     vocabulary='pmr2.vocab.manifest',
    #     required=False,
    # )

    # TODO ensure that the token is automatically scrubbed; pending the
    # actual implementation.
    bearer_token = zope.schema.ASCIILine(
        title=u"Bearer token",
        description=u"A bearer token used for accessing flatmap generation "
                     "service for the selected flatmap host; only necessary "
                     "if service requires one and the bearer token was not "
                     "configured in the registry for the named service. "
                     "The token assigned here should be scrubbed after the "
                     "flatmap generation is successfully sent.  When in "
                     "doubt, ensure this field is updated using an empty "
                     "value.",
        required=False,
    )

    flatmap_host = zope.schema.Choice(
        title=u'Flatmap Host',
        description=u'The flatmap host which this flatmap exposure file will '
                     'be processed and reside on.',
        vocabulary='pmr2.vocab.flatmap_hosts',
    )

    flatmap_host_root = zope.schema.ASCII(
        title=u'Flatmap Host Root',
        description=u'The host uri root that was most recently used',
    )

    initial_response = zope.schema.Text(
        title=u'Initial Response',
        description=u'The initial response JSON returned by the generation '
                     'request; currently it will reference both the PID of '
                     'the flatmap service worker for the current prototype.',
        required=False,
    )

    map_id = zope.schema.TextLine(
        title=u'Map ID',
        description=u'The map identifier on the flatmap host for this flatmap '
                     'exposure file view.',
        required=False,
    )


class ISDSNote(zope.interface.Interface):
    """
    SDS note.
    """


class IMapDataMakerUtility(zope.interface.Interface):
    """
    Marker interface for mapdatamaker utility
    """
