from typing import List
from django.core.exceptions import ValidationError
from django.template import Template, TemplateSyntaxError


class TemplateValidator:
    """Validator for email templates."""

    @staticmethod
    def validate_template_syntax(content: str) -> None:
        """Validate Django template syntax."""
        try:
            Template(content)
        except TemplateSyntaxError as e:
            raise ValidationError(f"Invalid template syntax: {str(e)}")

    @staticmethod
    def extract_variables(content: str) -> List[str]:
        """Extract variable names from template content."""
        import re

        pattern = r"\{\{\s*(\w+)\s*\}\}"
        return list(set(re.findall(pattern, content)))
