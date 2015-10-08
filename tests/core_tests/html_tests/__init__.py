from ..import RublonTestBase
from rublon.core.html.widget import RublonWidget


class RublonAbstractWidgetTests(RublonTestBase):

    def setUp(self):
        self.widget = RublonWidget()

    def test_create_attributes_string(self):
        result = self.widget.create_attributes_string({'key': 'value', 'zone': 'area'})
        assert 'key="value"' in result
        assert 'zone="area"' in result