from .widget import RublonWidget


class RublonLoginBox(RublonWidget):

    login_url = None
    size = None

    def __init__(self, login_url, size='small'):
        """Initializes Rublon Login Box"""
        self.login_url = login_url
        self.size = size

    def get_widget_attributes(self):
        """Widget's HTML iframe attributes."""
        return {
            'id': 'RublonLoginBoxWidget',
            'data-login-url': self.login_url,
            'data-size': self.size
        }