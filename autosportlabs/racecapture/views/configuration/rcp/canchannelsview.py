import kivy
kivy.require('1.9.0')
import os
from kivy.metrics import sp
from kivy.app import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.switch import Switch
from kivy.uix.spinner import SpinnerOption
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, NumericProperty
from garden_androidtabs import AndroidTabsBase, AndroidTabs
from iconbutton import IconButton
from settingsview import SettingsSwitch
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.config.rcpconfig import *
from autosportlabs.uix.layout.sections import SectionBoxLayout, HeaderSectionBoxLayout
from autosportlabs.racecapture.views.util.alertview import confirmPopup, choicePopup, editor_popup
from autosportlabs.racecapture.resourcecache.resourcemanager import ResourceCache
from fieldlabel import FieldLabel
from utils import *
from valuefield import FloatValueField, IntegerValueField
from mappedspinner import MappedSpinner
import copy

class LargeSpinnerOption(SpinnerOption):
    Builder.load_string("""
<LargeSpinnerOption>:
    font_size: self.height * 0.5
""")

class LargeMappedSpinner(MappedSpinner):
    Builder.load_string("""
<LargeMappedSpinner>:
    font_size: self.height * 0.4
    option_cls: 'LargeSpinnerOption'
""")

class LargeIntegerValueField(IntegerValueField):
    Builder.load_string("""
<LargeIntegerValueField>:
    font_size: self.height * 0.5
""")

class LargeFloatValueField(FloatValueField):
    Builder.load_string("""
<LargeFloatValueField>:
    font_size: self.height * 0.5
""")

class SymbolFieldLabel(FieldLabel):
    Builder.load_string("""
<SymbolFieldLabel>:
    font_size: self.height * 0.6
    font_name: 'resource/fonts/Roboto-Bold.ttf'
    shorten: False
""")

class CANChannelMappingTab(AnchorLayout, AndroidTabsBase):
    """
    Wrapper class to allow customization and styling
    """
    Builder.load_string("""
<CANChannelMappingTab>:
    canvas.before:
        Color:
            rgba: ColorScheme.get_dark_background()
        Rectangle:
            pos: self.pos
            size: self.size

    tab_font_name: "resource/fonts/ASL_light.ttf"
    tab_font_size: sp(20)    
""")
    tab_font_name = StringProperty()
    tab_font_size = NumericProperty()

    def on_tab_font_name(self, instance, value):
        self.tab_label.font_name = value

    def on_tab_font_size(self, instance, value):
        self.tab_label.font_size = value

class CANChannelCustomizationTab(CANChannelMappingTab):
    Builder.load_string("""
<CANChannelCustomizationTab>:
    text: 'Channel'
    AnchorLayout:
        size_hint_y: 0.33
        BoxLayout:
            spacing: dp(10)
            SectionBoxLayout:
                size_hint_x: 0.5
                ChannelNameSelectorView:
                    id: chan_id
                    on_channel: root.channel_selected(*args)
            SectionBoxLayout:
                size_hint_x: 0.5
                FieldLabel:
                    halign: 'right'
                    text: 'Sample Rate'
                SampleRateSpinner:
                    id: sr
""")

    def __init__(self, **kwargs):
        super(CANChannelCustomizationTab, self).__init__(**kwargs)
        self.register_event_type('on_channel')
        self._loaded = False

    def on_channel(self, channel_name):
        pass

    def channel_selected(self, value):
        if self._loaded:
            self.dispatch('on_channel', value.channel_config)

    def set_channel_filter_list(self, filter_list):
        self.ids.chan_id.filter_list = filter_list

    def init_view(self, channel_cfg, channels, max_sample_rate):
        self._loaded = False
        self.channel_cfg = channel_cfg

        channel_editor = self.ids.chan_id
        channel_editor.on_channels_updated(channels)
        channel_editor.setValue(self.channel_cfg)

        sample_rate_spinner = self.ids.sr
        sample_rate_spinner.set_max_rate(max_sample_rate)
        sample_rate_spinner.setFromValue(self.channel_cfg.sampleRate)
        sample_rate_spinner.bind(text=self.on_sample_rate)

        self._loaded = True

    def on_sample_rate(self, instance, value):
        if self._loaded:
            self.channel_cfg.sampleRate = instance.getValueFromKey(value)

class CANIDMappingTab(CANChannelMappingTab):
    Builder.load_string("""
<CANIDMappingTab>:
    text: 'CAN ID Match'
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            spacing: dp(10)            
            AnchorLayout:
                size_hint_x: 0.35
                SectionBoxLayout:
                    size_hint_y: 0.33
                    FieldLabel:
                        text: 'CAN bus'
                        halign: 'right'
                    LargeMappedSpinner:
                        id: can_bus_channel
                        on_text: root.on_can_bus(*args)

            AnchorLayout:
                size_hint_x: 0.65
                BoxLayout:
                    size_hint_y: 0.8
                    spacing: dp(20)
                    padding: (dp(20), dp(20))
                    orientation: 'vertical'
                    SectionBoxLayout:
                        FieldLabel:
                            size_hint_x: 0.3
                            text: 'CAN ID' 
                            halign: 'right'
    
                        LargeIntegerValueField:
                            id: can_id
                            size_hint_x: 0.7
                            on_text: root.on_can_id(*args)
    
                    SectionBoxLayout:
                        FieldLabel:
                            size_hint_x: 0.3
                            text: 'Mask'
                            halign: 'right'
    
                        LargeIntegerValueField:
                            id: mask
                            size_hint_x: 0.7
                            on_text: root.on_mask(*args)
""")

    def __init__(self, **kwargs):
        super(CANIDMappingTab, self).__init__(**kwargs)
        self._loaded = False

    def init_view(self, channel_cfg):
        self._loaded = False
        self.channel_cfg = channel_cfg
        self.ids.can_bus_channel.setValueMap({0: '1', 1: '2'}, '1')

        # CAN Channel
        self.ids.can_bus_channel.setFromValue(self.channel_cfg.mapping.can_bus)

        # CAN ID
        self.ids.can_id.text = str(self.channel_cfg.mapping.can_id)

        # CAN mask
        self.ids.mask.text = str(self.channel_cfg.mapping.can_mask)
        self._loaded = True

    def on_sample_rate(self, instance, value):
        if self._loaded:
            self.channel_cfg.sampleRate = instance.getValueFromKey(value)

    def on_can_bus(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.can_bus = instance.getValueFromKey(value)

    def on_can_id(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.can_id = int(value)

    def on_mask(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.can_mask = int(value)

class CANValueMappingTab(CANChannelMappingTab):
    Builder.load_string("""
<CANValueMappingTab>:
    text: 'Raw Value Mapping'
    
    BoxLayout:
        orientation: 'horizontal'
        spacing: dp(20)
        padding: (dp(20), dp(20))
        AnchorLayout:
            size_hint_x: 0.6        
            BoxLayout:
                size_hint_y: 0.33
                orientation: 'horizontal'
                spacing: dp(5)
                
                SectionBoxLayout:
                    size_hint_x: 0.33
                    FieldLabel:
                        text: 'Offset'
                        halign: 'right'
                    LargeMappedSpinner:
                        id: offset
                        on_text: root.on_mapping_offset(*args)
                SectionBoxLayout:
                    size_hint_x: 0.33             
                    FieldLabel:
                        halign: 'right'
                        text: 'Length'
                    LargeMappedSpinner:
                        id: length
                        on_text: root.on_mapping_length(*args)
        BoxLayout:
            anchor_x: 'right'
            orientation: 'vertical'
            size_hint_x: 0.4       
            spacing: dp(10)
            padding: (dp(10), dp(10))
            SectionBoxLayout:
                FieldLabel:
                    text: 'Bit Mode'
                    halign: 'right'
                CheckBox:
                    id: bitmode
                    on_active: root.on_bit_mode(*args)
            SectionBoxLayout:
                FieldLabel:
                    text: 'Endian'
                    halign: 'right'
                MappedSpinner:
                    id: endian
                    on_text: root.on_endian(*args)
""")

    def __init__(self, **kwargs):
        super(CANValueMappingTab, self).__init__(**kwargs)
        self._loaded = False

    def init_view(self, channel_cfg):
        self._loaded = False
        self.channel_cfg = channel_cfg
        self.ids.endian.setValueMap({0: 'Big (MSB)', 1: 'Little (LSB)'}, 'Big (MSB)')
        self.update_mapping_spinners()

        # CAN offset
        self.ids.offset.setFromValue(self.channel_cfg.mapping.offset)

        # CAN length
        self.ids.length.setFromValue(self.channel_cfg.mapping.length)

        # Bit Mode
        self.ids.bitmode.active = self.channel_cfg.mapping.bit_mode

        # Endian
        self.ids.endian.setFromValue(self.channel_cfg.mapping.endian)

        self._loaded = True

    def update_mapping_spinners(self):
        bit_mode = self.channel_cfg.mapping.bit_mode
        self.set_mapping_choices(bit_mode)

    def set_mapping_choices(self, bit_mode):
        offset_choices = 63 if bit_mode else 7
        length_choices = 32 if bit_mode else 4
        self.ids.offset.setValueMap(self.create_bit_choices(0, offset_choices), '0')
        self.ids.length.setValueMap(self.create_bit_choices(1, length_choices), '1')

    def create_bit_choices(self, starting, max_choices):
        bit_choices = {}
        for i in range(starting, max_choices + 1):
            bit_choices[i] = str(i)
        return bit_choices

    def on_bit_mode(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.bit_mode = self.ids.bitmode.active
            self.update_mapping_spinners()

    def on_mapping_offset(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.offset = instance.getValueFromKey(value)

    def on_mapping_length(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.length = instance.getValueFromKey(value)

    def on_endian(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.endian = instance.getValueFromKey(value)

class CANFormulaMappingTab(CANChannelMappingTab):
    Builder.load_string("""
<CANFormulaMappingTab>:
    text: 'Conversion Formula'

    AnchorLayout:
        size_hint_y: 0.5
        SectionBoxLayout:
            orientation: 'horizontal'
            spacing: dp(5)
            FieldLabel:
                size_hint_x: 0.1
                halign: 'right'
                text: 'Raw'
            SymbolFieldLabel:
                size_hint_x: 0.1
                halign: 'center'
                text: u' \u00D7 '
            AnchorLayout:
                size_hint_x: 0.2
                LargeFloatValueField:
                    id: multiplier
                    size_hint_y: 0.7
                    on_text: root.on_multiplier(*args)
            SymbolFieldLabel:
                halign: 'center'
                text: u' \u00F7 '
                size_hint_x: 0.1
            AnchorLayout:
                size_hint_x: 0.2
                LargeFloatValueField:
                    id: divider
                    size_hint_y: 0.7
                    on_text: root.on_divider(*args)
            SymbolFieldLabel:
                text: ' + '
                halign: 'center'
                size_hint_x: 0.1
            AnchorLayout:
                size_hint_x: 0.2
                LargeFloatValueField:
                    id: adder
                    size_hint_y: 0.7
                    on_text: root.on_adder(*args)
        
    #            BoxLayout:
    #                orientation: 'horizontal'
    #                spacing: dp(5)
    #                FieldLabel:
    #                    halign: 'right'
    #                    size_hint_x: 0.3
    #                    text: 'Conversion Filter'
    #                MappedSpinner:
    #                    id: filters     
    #                    size_hint_x: 0.7
    #                    on_text: root.on_filter(*args)
""")

    def __init__(self, **kwargs):
        super(CANFormulaMappingTab, self).__init__(**kwargs)
        self._loaded = False

    def init_view(self, channel_cfg):
        self._loaded = False
        self.channel_cfg = channel_cfg

        # Disable for the initial release
        # self.ids.filters.setValueMap(self.can_filters.filters, self.can_filters.default_value)

        # Multiplier
        self.ids.multiplier.text = str(self.channel_cfg.mapping.multiplier)

        # Divider
        self.ids.divider.text = str(self.channel_cfg.mapping.divider)

        # Adder
        self.ids.adder.text = str(self.channel_cfg.mapping.adder)

        # Conversion Filter ID
        # Disable for initial release
        # self.ids.filters.setFromValue(self.channel_cfg.mapping.conversion_filter_id)

        self._loaded = True


    def on_multiplier(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.multiplier = float(value)

    def on_divider(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.divider = float(value)

    def on_adder(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.adder = float(value)

    def on_filter(self, instance, value):
        if self._loaded:
            self.channel_cfg.mapping.conversion_filter_id = instance.getValueFromKey(value)



class CANChannelConfigView(BoxLayout):

    Builder.load_string("""
<CANChannelConfigView>:
    canvas.before:
        Color:
            rgba: ColorScheme.get_accent()
        Rectangle:
            pos: self.pos
            size: self.size
    AndroidTabs:
        tab_indicator_color: ColorScheme.get_light_primary()
        id: tabs
""")

    def __init__(self, **kwargs):
        super(CANChannelConfigView, self).__init__(**kwargs)
        self.can_channel_customization_tab = CANChannelCustomizationTab()
        self.can_id_tab = CANIDMappingTab()
        self.can_value_map_tab = CANValueMappingTab()
        self.can_formula_tab = CANFormulaMappingTab()
        self.init_tabs()

    def init_tabs(self):
        self.ids.tabs.add_widget(self.can_channel_customization_tab)
        self.ids.tabs.add_widget(self.can_id_tab)
        self.ids.tabs.add_widget(self.can_value_map_tab)
        self.ids.tabs.add_widget(self.can_formula_tab)

    def init_config(self, index, channel_cfg, can_filters, max_sample_rate, channels):
        self.channel_index = index
        self.channel_cfg = channel_cfg
        self.can_filters = can_filters
        self.max_sample_rate = max_sample_rate
        self.channels = channels
        self.load_tabs()

    def load_tabs(self):
        self.can_channel_customization_tab.init_view(self.channel_cfg, self.channels, self.max_sample_rate)
        self.can_id_tab.init_view(self.channel_cfg)
        self.can_value_map_tab.init_view(self.channel_cfg)
        self.can_formula_tab.init_view(self.channel_cfg)

class CANFilters(object):
    filters = None
    default_value = None
    def __init__(self, base_dir, **kwargs):
        super(CANFilters, self).__init__(**kwargs)
        self.load_CAN_filters(base_dir)


    def load_CAN_filters(self, base_dir):
        if self.filters != None:
            return
        try:
            self.filters = {}
            can_filters_json = open(os.path.join(base_dir, 'resource', 'settings', 'can_channel_filters.json'))
            can_filters = json.load(can_filters_json)['can_channel_filters']
            for k in sorted(can_filters.iterkeys()):
                if not self.default_value:
                    self.default_value = k
                self.filters[int(k)] = can_filters[k]
        except Exception as detail:
            raise Exception('Error loading CAN filters: ' + str(detail))

CAN_CHANNEL_VIEW_KV = """
<CANChannelView>:
    size_hint_y: None
    height: dp(30)
    orientation: 'horizontal'
    FieldLabel:
        id: name
        size_hint_x: 0.18
    FieldLabel:
        id: sample_rate
        size_hint_x: 0.10
    FieldLabel:
        id: can_id
        size_hint_x: 0.14
    FieldLabel:
        id: can_offset_len
        size_hint_x: 0.15
    FieldLabel:
        size_hint_x: 0.30
        id: can_formula
    IconButton:
        size_hint_x: 0.09        
        text: u'\uf044'
        on_release: root.on_customize()
    IconButton:
        size_hint_x: 0.09        
        text: u'\uf014'
        on_release: root.on_delete()
"""

class CANChannelView(BoxLayout):
    Builder.load_string(CAN_CHANNEL_VIEW_KV)

    def __init__(self, channel_index, channel_cfg, max_sample_rate, channels, **kwargs):
        super(CANChannelView, self).__init__(**kwargs)
        self.channel_index = channel_index
        self.channel_cfg = channel_cfg
        self.max_sample_rate = max_sample_rate
        self.channels = channels
        self.register_event_type('on_delete_channel')
        self.register_event_type('on_customize_channel')
        self.register_event_type('on_modified')
        self._loaded = False
        self.set_channel()

    def on_modified(self):
        pass

    def on_delete_channel(self, channel_index):
        pass

    def on_customize_channel(self, channel_index):
        pass

    def on_delete(self):
        self.dispatch('on_delete_channel', self.channel_index)

    def on_customize(self):
        self.dispatch('on_customize_channel', self.channel_index)

    def set_channel(self):
        self.ids.name.text = self.channel_cfg.name

        self.ids.sample_rate.text = '{} Hz'.format(self.channel_cfg.sampleRate)

        can_mapping = self.channel_cfg.mapping
        self.ids.can_id.text = '{}'.format(can_mapping.can_id)

        self.ids.can_offset_len.text = u'{}({})'.format(can_mapping.offset, can_mapping.length)

        sign = '-' if can_mapping.adder < 0 else '+'
        self.ids.can_formula.text = u'\u00D7 {} \u00F7 {} {} {}'.format(can_mapping.multiplier, can_mapping.divider, sign, abs(can_mapping.adder))
        self._loaded = True

class CANPresetResourceCache(ResourceCache):
    preset_url = "http://podium.live/api/v1/can_presets"
    preset_name = 'can_presets'

    def __init__(self, settings, base_dir, **kwargs):
        default_preset_dir = os.path.join(base_dir, 'resource', self.preset_name)
        super(CANPresetResourceCache, self).__init__(settings, self.preset_url, self.preset_name, default_preset_dir, **kwargs)

CAN_CHANNELS_VIEW_KV = """
<CANChannelsView>:
    spacing: dp(20)
    orientation: 'vertical'
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.20
        SettingsView:
            size_hint_y: 0.6
            id: can_channels_enable
            label_text: 'CAN channels'
            help_text: ''
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.4        
            BoxLayout:
                size_hint_x: 0.8
            LabelIconButton:
                size_hint_x: 0.2
                id: load_preset
                title: 'Presets'
                icon_size: self.height * 0.7
                title_font_size: self.height * 0.5
                icon: u'\uf150'
                on_press: root.load_preset_view()
        
    BoxLayout:
        size_hint_y: 0.70
        orientation: 'vertical'        
        HSeparator:
            text: 'CAN Channels'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.1
            padding: [dp(5), dp(0)]            
            FieldLabel:
                text: 'Channel'
                halign: 'left'
                size_hint_x: 0.18
            FieldLabel:
                text: 'Rate'
                halign: 'left'
                size_hint_x: 0.10
                
            FieldLabel:
                text: 'CAN ID'
                size_hint_x: 0.14
            FieldLabel:
                text: 'Offset(Len)'
                size_hint_x: 0.15
            FieldLabel:
                text: 'Formula'
                size_hint_x: 0.30
            FieldLabel:
                text: ''
                size_hint_x: 0.18
            
        AnchorLayout:                
            AnchorLayout:
                ScrollContainer:
                    canvas.before:
                        Color:
                            rgba: 0.05, 0.05, 0.05, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size                
                    id: scroller
                    size_hint_y: 0.95
                    do_scroll_x:False
                    do_scroll_y:True
                    GridLayout:
                        id: can_grid
                        padding: [dp(5), dp(5)]                        
                        spacing: [dp(0), dp(10)]
                        size_hint_y: None
                        height: max(self.minimum_height, scroller.height)
                        cols: 1
                FieldLabel:
                    halign: 'center'
                    id: list_msg
                    text: ''
            AnchorLayout:
                anchor_y: 'bottom'
                IconButton:
                    size_hint: (None, None)
                    height: root.height * .12
                    text: u'\uf055'
                    color: ColorScheme.get_accent()
                    on_release: root.on_add_can_channel()
                    disabled: True
                    id: add_can_channel
"""
class CANChannelsView(BaseConfigView):
    DEFAULT_CAN_SAMPLE_RATE = 1
    can_channels_cfg = None
    max_sample_rate = 0
    can_grid = None
    can_channels_settings = None
    can_filters = None
    _popup = None
    Builder.load_string(CAN_CHANNELS_VIEW_KV)

    def __init__(self, **kwargs):
        super(CANChannelsView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')
        self.can_grid = self.ids.can_grid
        self._base_dir = kwargs.get('base_dir')
        self.max_can_channels = 0
        can_channels_enable = self.ids.can_channels_enable
        can_channels_enable.bind(on_setting=self.on_can_channels_enabled)
        can_channels_enable.setControl(SettingsSwitch())
        self.update_view_enabled()
        self.can_filters = CANFilters(self._base_dir)
        self._resource_cache = None

    def get_resource_cache(self):
        if self._resource_cache is None:
            self._resource_cache = CANPresetResourceCache(self.settings, self._base_dir)
        return self._resource_cache

    def on_modified(self, *args):
        if self.can_channels_cfg:
            self.can_channels_cfg.stale = True
            self.dispatch('on_config_modified', *args)

    def on_can_channels_enabled(self, instance, value):
        if self.can_channels_cfg:
            self.can_channels_cfg.enabled = value
            self.dispatch('on_modified')

    def on_config_updated(self, rc_cfg):
        can_channels_cfg = rc_cfg.can_channels
        max_sample_rate = rc_cfg.capabilities.sample_rates.sensor
        max_can_channels = rc_cfg.capabilities.channels.can_channel
        self.ids.can_channels_enable.setValue(can_channels_cfg.enabled)

        self.reload_can_channel_grid(can_channels_cfg, max_sample_rate)
        self.can_channels_cfg = can_channels_cfg
        self.max_sample_rate = max_sample_rate
        self.max_can_channels = max_can_channels
        self.update_view_enabled()

    def update_view_enabled(self):
        add_disabled = True
        if self.can_channels_cfg:
            if len(self.can_channels_cfg.channels) < self.max_can_channels:
                add_disabled = False

        self.ids.add_can_channel.disabled = add_disabled

    def _refresh_channel_list_notice(self):
        cfg = self.can_channels_cfg
        if cfg is not None:
            channel_count = len(cfg.channels)
            self.ids.list_msg.text = 'No channels defined. Press (+) to map a CAN channel' if channel_count == 0 else ''

    def reload_can_channel_grid(self, can_channels_cfg, max_sample_rate):
        self.can_grid.clear_widgets()
        channel_count = len(can_channels_cfg.channels)
        for i in range(channel_count):
            channel_cfg = can_channels_cfg.channels[i]
            self.append_can_channel(i, channel_cfg, max_sample_rate)
        self.update_view_enabled()
        self._refresh_channel_list_notice()

    def append_can_channel(self, index, channel_cfg, max_sample_rate):
        channel_view = CANChannelView(index, channel_cfg, max_sample_rate, self.channels)
        channel_view.bind(on_delete_channel=self.on_delete_channel)
        channel_view.bind(on_customize_channel=self.on_customize_channel)
        channel_view.bind(on_modified=self.on_modified)
        self.can_grid.add_widget(channel_view)

    def on_add_can_channel(self):
        if (self.can_channels_cfg):
            can_channel = CANChannel()
            can_channel.sampleRate = self.DEFAULT_CAN_SAMPLE_RATE
            new_channel_index = self.add_can_channel(can_channel)
            self._customize_channel(new_channel_index)

    def add_can_channel(self, can_channel):
        self.can_channels_cfg.channels.append(can_channel)
        new_channel_index = len(self.can_channels_cfg.channels) - 1
        self.append_can_channel(new_channel_index, can_channel, self.max_sample_rate)
        self.update_view_enabled()
        self.dispatch('on_modified')
        return new_channel_index

    def _delete_all_channels(self):
        del self.can_channels_cfg.channels[:]
        self.reload_can_channel_grid(self.can_channels_cfg, self.max_sample_rate)
        self.dispatch('on_modified')

    def _delete_can_channel(self, channel_index):
        del self.can_channels_cfg.channels[channel_index]
        self.reload_can_channel_grid(self.can_channels_cfg, self.max_sample_rate)
        self.dispatch('on_modified')

    def on_delete_channel(self, instance, channel_index):
        popup = None
        def _on_answer(instance, answer):
            if answer:
                self._delete_can_channel(channel_index)
            popup.dismiss()
        popup = confirmPopup('Confirm', 'Delete CAN Channel?', _on_answer)

    def _replace_config(self, to_cfg, from_cfg):
        to_cfg.__dict__.update(from_cfg.__dict__)

    def popup_dismissed(self, *args):
        self.reload_can_channel_grid(self.can_channels_cfg, self.max_sample_rate)

    def _customize_channel(self, channel_index):
        content = CANChannelConfigView()
        working_channel_cfg = copy.deepcopy(self.can_channels_cfg.channels[channel_index])
        content.init_config(channel_index, working_channel_cfg, self.can_filters, self.max_sample_rate, self.channels)

        def _on_answer(instance, answer):
            if answer:
                self._replace_config(self.can_channels_cfg.channels[content.channel_index], working_channel_cfg)
                self.dispatch('on_modified')

            self.reload_can_channel_grid(self.can_channels_cfg, self.max_sample_rate)
            popup.dismiss()

        popup = editor_popup('Customize CAN mapping', content, _on_answer, size_hint=(0.7, 0.75))

    def on_customize_channel(self, instance, channel_index):
        self._customize_channel(channel_index)

    def on_preset_selected(self, instance, preset_id):
        popup = None
        def _on_answer(instance, answer):
            if answer == True:
                self._delete_all_channels()
            self._import_preset(preset_id)
            popup.dismiss()

        if len(self.can_channels_cfg.channels) > 0:
            popup = choicePopup('Confirm', 'Overwrite or append existing channels?', 'Overwrite', 'Append', _on_answer)
        else:
            self._import_preset(preset_id)

    def _import_preset(self, preset_id):
        resource_cache = self.get_resource_cache()
        preset = resource_cache.resources.get(preset_id)
        if preset:
            for channel_json in preset['channels']:
                new_channel = CANChannel()
                new_channel.from_json_dict(channel_json)
                self.add_can_channel(new_channel)
        self._refresh_channel_list_notice()

    def load_preset_view(self):
        content = PresetBrowserView(self.get_resource_cache())
        content.bind(on_preset_selected=self.on_preset_selected)
        content.bind(on_preset_close=lambda *args:popup.dismiss())
        popup = Popup(title='Import a preset configuration', content=content, size_hint=(0.5, 0.75))
        popup.bind(on_dismiss=self.popup_dismissed)
        popup.open()

PRESET_ITEM_VIEW_KV = """
<PresetItemView>:
    canvas.before:
        Color:
            rgba: 0.01, 0.01, 0.01, 1
        Rectangle:
            pos: self.pos
            size: self.size             

    orientation: 'vertical'
    size_hint_y: None
    height: dp(200)
    padding: (dp(20), dp(0))
    spacing: dp(10)
    FieldLabel:
        id: title
        size_hint_y: 0.1
    BoxLayout:
        spacing: dp(10)
        size_hint_y: 0.85
        orientation: 'horizontal'
        AnchorLayout:
            size_hint_x: 0.75
            Image:
                id: image
            AnchorLayout:
                anchor_y: 'bottom'
                BoxLayout:
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 0.7
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    size_hint_y: 0.3
                    FieldLabel:
                        halign: 'left'
                        id: notes

        AnchorLayout:
            size_hint_x: 0.25
            anchor_x: 'center'
            anchor_y: 'center'
            LabelIconButton:
                size_hint_x: 1
                size_hint_y: 0.3
                id: load_preset
                title: 'Select'
                icon_size: self.height * 0.7
                title_font_size: self.height * 0.5
                icon: u'\uf046'
                on_press: root.select_preset()
"""
class PresetItemView(BoxLayout):
    Builder.load_string(PRESET_ITEM_VIEW_KV)

    def __init__(self, preset_id, name, notes, image_path, **kwargs):
        super(PresetItemView, self).__init__(**kwargs)
        self.preset_id = preset_id
        self.ids.title.text = name
        self.ids.notes.text = notes
        self.ids.image.source = image_path
        self.register_event_type('on_preset_selected')

    def select_preset(self):
        self.dispatch('on_preset_selected', self.preset_id)

    def on_preset_selected(self, preset_id):
        pass

PRESET_BROWSER_VIEW_KV = """
<PresetBrowserView>:
    orientation: 'vertical'
    spacing: dp(10)
    ScrollView:
        size_hint_y: 0.85
        canvas.before:
            Color:
                rgba: 0.05, 0.05, 0.05, 1
            Rectangle:
                pos: self.pos
                size: self.size
        id: scroller
        size_hint_y: 0.95
        do_scroll_x:False
        do_scroll_y:True
        GridLayout:
            id: preset_grid
            spacing: [dp(10), dp(10)]
            size_hint_y: None
            height: max(self.minimum_height, scroller.height)
            cols: 1
    IconButton:
        size_hint_y: 0.15
        text: u'\uf00d'
        on_press: root.on_close()
"""

class PresetBrowserView(BoxLayout):
    presets = None
    Builder.load_string(PRESET_BROWSER_VIEW_KV)

    def __init__(self, resource_cache, **kwargs):
        super(PresetBrowserView, self).__init__(**kwargs)
        self.register_event_type('on_preset_close')
        self.register_event_type('on_preset_selected')
        self.resource_cache = resource_cache
        self.init_view()

    def on_preset_close(self):
        pass

    def on_preset_selected(self, preset_id):
        pass

    def init_view(self):
        self.refresh_view()

    def refresh_view(self):
        for k, v in self.resource_cache.resources.iteritems():
            name = v.get('name', '')
            notes = v.get('notes', '')
            self.add_preset(k, name, notes)

    def add_preset(self, preset_id, name, notes):
        image_path = self.resource_cache.resource_image_paths.get(preset_id)
        preset_view = PresetItemView(preset_id, name, notes, image_path)
        preset_view.bind(on_preset_selected=self.preset_selected)
        self.ids.preset_grid.add_widget(preset_view)

    def preset_selected(self, instance, preset_id):
        self.dispatch('on_preset_selected', preset_id)
        self.dispatch('on_preset_close')

    def on_close(self, *args):
        self.dispatch('on_preset_close')
