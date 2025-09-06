import logging
from typing import Dict, Tuple, Any
from django.template import Template, Context
from django.template.loader import render_to_string

logger = logging.getLogger("mailer")


class TemplateService:
    """Email template service"""

    def render_template(
        self, template_name: str, context: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Render a template with context and return HTML and Plain Text
        """
        try:
            # Render HTML
            html_template = f"emails/{template_name}.html"
            html_content = render_to_string(html_template, context)

            # Render Plain Text (if not provided)
            plain_content = ""
            try:
                plain_template = f"emails/{template_name}.txt"
                plain_content = render_to_string(plain_template, context)
            except:
                # Extract plain text from HTML if not provided
                plain_content = self._html_to_plain_text(html_content)

            return html_content, plain_content

        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            raise

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a string template with context
        """
        try:
            template = Template(template_string)
            rendered = template.render(Context(context))
            return rendered
        except Exception as e:
            logger.error(f"Failed to render string template: {str(e)}")
            raise

    def _html_to_plain_text(self, html_content: str) -> str:
        """
        Render HTML to plain text
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, "html.parser")

        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract text
        text = soup.get_text()

        # Remove extra whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        return text
