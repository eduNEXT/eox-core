"""
Models used in eox-core.
"""
from django.db import models


class Redirection(models.Model):
    """
    This object stores the redirects for a domain
    """

    HTTP = 'http'
    HTTPS = 'https'

    SCHEME = (
        (HTTP, 'http'),
        (HTTPS, 'https'),
    )

    STATUS = (
        (301, 'Temporary'),
        (302, 'Permanent'),
    )

    domain = models.CharField(max_length=253, db_index=True,
                              help_text='use only the domain name, e.g. cursos.edunext.co')
    target = models.CharField(max_length=253)
    scheme = models.CharField(max_length=5, choices=SCHEME, default=HTTP)
    status = models.IntegerField(choices=STATUS, default=301)

    class Meta:  # pylint: disable=no-init
        """
        Model meta class.
        """
        # Note to ops: The table already exists under a different name due to the migration from EOE.
        db_table = 'edunext_redirection'

    def __unicode__(self):
        return u"Redirection from {} to {}. Protocol {}. Status {}".format(
            self.domain,
            self.target,
            self.scheme,
            self.status,
        )
