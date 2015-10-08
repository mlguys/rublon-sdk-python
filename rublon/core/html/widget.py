import six
from rublon.functions import htmlspecialchars


class RublonWidget(object):
    """Abstract base class for widgets"""

    # Device Widget CSS attributes.
    WIDGET_CSS_FONT_COLOR = 'font-color'
    WIDGET_CSS_FONT_SIZE = 'font-size'
    WIDGET_CSS_FONT_FAMILY = 'font-family'
    WIDGET_CSS_BACKGROUND_COLOR = 'background-color'

    def __str__(self):
        """Get iframe to load the Device Widget."""
        merged_attrs = self.get_widget_attributes()
        merged_attrs.update(self.get_widget_css_attributes_data())
        return '<iframe {0}></iframe>'.format(self.create_attributes_string(
            merged_attrs
        ))

    def create_attributes_string(self, attrs):
        """Creates HTML attributes string."""
        escaped = lambda key, value: '{0}="{1}"'.format(htmlspecialchars(key), htmlspecialchars(value))
        return ' '.join([escaped(key, value) for key, value in six.iteritems(attrs)])

    def get_widget_css_attributes_data(self):
        result = {}
        for name, value in six.iteritems(self.get_widget_css_attributes()):
            result['data-{0}'.format(name)] = value
        return result

    def get_widget_css_attributes(self):
        return {}

    def get_widget_attributes(self):
        pass