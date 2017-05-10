from glanceclient import Client as GlanceClient
from connections.connection import Connection


class GlanceConnection(Connection):
    """
    GlanceConnection module that contain a GlanceClient connection
    """
    def __init__(self, **kwargs):
        """
        :param kwargs: *version = version of GlanceClient
        *region_name = region name of GlanceClient
        """
        super().__init__(**kwargs)
        self._connection = GlanceClient(version=kwargs['version'], session=self.authentication.session,
                                        region_name=self.region_name)

    @property
    def region(self):
        """
        Region property of image_region Authentication

        :return: None or set content all region property
        """
        return self.authentication.image_region

    @property
    def endpoints(self):
        """
        Endpoints property of image Authentication

        :return: None or dict content endpoints
        """
        return self.authentication.image
