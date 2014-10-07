import kivy
kivy.require('1.8.0')
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.app import Builder
from kivy.metrics import dp
from utils import kvFind
from kivy.properties import NumericProperty
from autosportlabs.racecapture.views.dashboard.widgets.fontgraphicalgauge import FontGraphicalGauge

Builder.load_file('autosportlabs/racecapture/views/dashboard/widgets/roundgauge.kv')

class RoundGauge(AnchorLayout, FontGraphicalGauge):
    
    def __init__(self, **kwargs):
        super(RoundGauge, self).__init__(**kwargs)
        self.initWidgets()
            
    def initWidgets(self):
        pass
                                        
    def on_title(self, instance, value):
        view = self.titleView

        view.text = str(value)
        self._label = value
        