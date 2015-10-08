from .widget import RublonWidget


class RublonSubscribeWidget(RublonWidget):

    def get_widget_attributes(self):
        """Subscribe Widget HTML iframe attributes."""
        return {
            'class': 'rublon-subscribe-widget'
        }