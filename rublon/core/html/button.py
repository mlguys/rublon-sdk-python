from .widget import RublonWidget
from rublon.functions import htmlspecialchars


class RublonButton(RublonWidget):
    """Rublon button class.

    This class can be utilized to prepare a HTML container
    for the Rublon buttons. The containers embedded in the website
    will be filled with proper Rublon buttons once the consumer script
    is executed."""

    """Default CSS class of the button."""
    ATTR_CLASS = 'rublon-button'

    """Prefix of the button's CSS "size" class."""
    ATTR_CLASS_SIZE_PREFIX = 'rublon-button-size-'

    """Prefix of the button's CSS "color" class."""
    ATTR_CLASS_COLOR_PREFIX = 'rublon-button-color-'

    """HTML attribute name to put the consumer params."""
    ATTR_CONSUMER_PARAMS = 'data-rublonconsumerparams'

    # Available sizes
    SIZE_MINI = 'mini'
    SIZE_SMALL = 'small'
    SIZE_MEDIUM = 'medium'
    SIZE_LARGE = 'large'

    # Available colors
    COLOR_DARK = 'dark'
    COLOR_LIGHT = 'light'

    """Rublon instance.

    An istance of the Rublon class or its descendant.
    Necessary for the class to work.
    """
    rublon = None

    """Label of the button.

    Label displayed on the button and as its "title" attribute."""
    label = None

    """Size of the button.

    One of the predefined button size constants."""
    size = None

    """Color of the button.

    One of the predefined button color constants."""
    color = None

    """HTML attributes of the button's container.

    Any additional HTML attributes that will be added to the
    button upon its creation, e.g. class, style, data-attributes."""
    attributes = {}

    """HTML content of the button."""
    content = '<a href="https://rublon.com/">Rublon</a>'

    def __init__(self, rublon):
        self.rublon = rublon
        self.set_size(self.SIZE_MEDIUM)
        self.set_color(self.COLOR_DARK)

    def __str__(self):
        """Convert object into string.

        Returns HTML container of the button that can be embedded in the website."""
        attributes = self.attributes

        class_parts = [self.ATTR_CLASS]
        if attributes.get('class'):
            class_parts.append(attributes['class'])

        class_parts.append(self.ATTR_CLASS_SIZE_PREFIX + self.get_size())
        class_parts.append(self.ATTR_CLASS_COLOR_PREFIX + self.get_color())

        attributes['class'] += ' '.join(class_parts)

        if self.get_label():
            attributes['title'] = self.get_label()

        result = '<div {0}>{1}</div>'.format(
            ' '.join(['{0}="{1}"'.format(key, htmlspecialchars(value)) for key, value in attributes]),
            self.get_content()
        )

        return result

    def get_content(self):
        """Get HTML content of the button."""
        return self.content

    def set_content(self, content):
        """Set HTML content of the button."""
        self.content = content
        return self

    def set_label(self, label):
        """Set label of the button.

        Button label property setter."""
        self.label = label
        return self

    def get_label(self):
        """Get label of the button.

        Button label property getter."""
        return self.label

    def set_size(self, size):
        """Set size of the button.

        Button size property setter.
        Get available size from RublonButton::SIZE_... constant."""
        self.size = size
        return self

    def get_size(self):
        """Get size of the button.

        Button size property getter."""
        return self.size

    def set_color(self, color):
        """Set color of the button.

        Button color property setter.
        Get available color from RublonButton::COLOR_... constant."""
        self.color = color
        return self

    def get_color(self):
        """Get color of the button.

        Button color property getter."""
        return self.color

    def set_attribute(self, name, value):
        """Set HTML attribute of the button's container.

        Add a single HTML attribute to the button's container."""
        self.attributes[name] = value
        return self

    def get_attribute(self, name):
        """Get HTML attribute of the button's container.

        Returns the button's container single HTML attribute.
        Null if the attribute doesn't exist."""
        return self.attributes.get(name)

    def get_rublon(self):
        """Get Rublon instance."""
        return self.rublon







