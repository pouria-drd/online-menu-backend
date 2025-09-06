from django.db import models


class EmailTemplateManager(models.Manager):
    """A manager for EmailTemplateModel"""

    def active(self):
        """Get active templates"""
        return self.filter(is_active=True)

    def get_by_type(self, template_type):
        """Get template by type"""
        return self.active().filter(template_type=template_type).first()

    def get_by_name(self, name):
        """Get template by name"""
        return self.active().filter(name=name).first()
