from .widget import RublonWidget


class RublonBadge(RublonWidget):

    def get_widget_attributes(self):
        return {
            'id': 'RublonBadgeWidget'
        }