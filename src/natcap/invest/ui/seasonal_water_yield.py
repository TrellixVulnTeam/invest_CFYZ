# coding=UTF-8

from natcap.invest.ui import model, inputs
from natcap.invest.seasonal_water_yield import seasonal_water_yield


class SeasonalWaterYield(model.Model):
    label = u'Seasonal Water Yield'
    target = staticmethod(seasonal_water_yield.execute)
    validator = staticmethod(seasonal_water_yield.validate)
    localdoc = u'../documentation/seasonalwateryield.html'

    def __init__(self):
        model.Model.__init__(self)

        self.threshold_flow_accumulation = inputs.Text(
            args_key=u'threshold_flow_accumulation',
            helptext=(
                u"The number of upstream cells that must flow into a "
                u"cell before it's considered part of a stream such "
                u"that retention stops and the remaining export is "
                u"exported to the stream.  Used to define streams from "
                u"the DEM."),
            label=u'Threshold Flow Accumulation',
            validator=self.validator)
        self.add_input(self.threshold_flow_accumulation)
        self.et0_dir = inputs.Folder(
            args_key=u'et0_dir',
            helptext=(
                u"The selected folder has a list of ET0 files with a "
                u"specified format."),
            label=u'ET0 Directory',
            validator=self.validator)
        self.add_input(self.et0_dir)
        self.precip_dir = inputs.Folder(
            args_key=u'precip_dir',
            helptext=(
                u"The selected folder has a list of monthly "
                u"precipitation files with a specified format."),
            label=u'Precipitation Directory',
            validator=self.validator)
        self.add_input(self.precip_dir)
        self.dem_raster_path = inputs.File(
            args_key=u'dem_raster_path',
            helptext=(
                u"A GDAL-supported raster file with an elevation value "
                u"for each cell.  Make sure the DEM is corrected by "
                u"filling in sinks, and if necessary burning "
                u"hydrographic features into the elevation model "
                u"(recommended when unusual streams are observed.) See "
                u"the 'Working with the DEM' section of the InVEST "
                u"User's Guide for more information."),
            label=u'Digital Elevation Model (Raster)',
            validator=self.validator)
        self.add_input(self.dem_raster_path)
        self.lulc_raster_path = inputs.File(
            args_key=u'lulc_raster_path',
            helptext=(
                u"A GDAL-supported raster file, with an integer LULC "
                u"code for each cell."),
            label=u'Land-Use/Land-Cover (Raster)',
            validator=self.validator)
        self.add_input(self.lulc_raster_path)
        self.soil_group_path = inputs.File(
            args_key=u'soil_group_path',
            helptext=(
                u"Map of SCS soil groups (A, B, C, or D) mapped to "
                u"integer values (1, 2, 3, or 4) used in combination of "
                u"the LULC map to compute the CN map."),
            label=u'Soil Group (Raster)',
            validator=self.validator)
        self.add_input(self.soil_group_path)
        self.aoi_path = inputs.File(
            args_key=u'aoi_path',
            label=u'AOI/Watershed (Vector)',
            validator=self.validator)
        self.add_input(self.aoi_path)
        self.biophysical_table_path = inputs.File(
            args_key=u'biophysical_table_path',
            helptext=(
                u"A CSV table containing model information "
                u"corresponding to each of the land use classes in the "
                u"LULC raster input.  It must contain the fields "
                u"'lucode', and 'Kc'."),
            label=u'Biophysical Table (CSV)',
            validator=self.validator)
        self.add_input(self.biophysical_table_path)
        self.rain_events_table_path = inputs.File(
            args_key=u'rain_events_table_path',
            label=u'Rain Events Table (CSV)',
            validator=self.validator)
        self.add_input(self.rain_events_table_path)
        self.alpha_m = inputs.Text(
            args_key=u'alpha_m',
            label=u'alpha_m Parameter',
            validator=self.validator)
        self.add_input(self.alpha_m)
        self.beta_i = inputs.Text(
            args_key=u'beta_i',
            label=u'beta_i Parameter',
            validator=self.validator)
        self.add_input(self.beta_i)
        self.gamma = inputs.Text(
            args_key=u'gamma',
            label=u'gamma Parameter',
            validator=self.validator)
        self.add_input(self.gamma)
        self.climate_zone_container = inputs.Container(
            args_key=u'user_defined_climate_zones',
            expandable=True,
            label=u'Climate Zones (Advanced)')
        self.add_input(self.climate_zone_container)
        self.climate_zone_table_path = inputs.File(
            args_key=u'climate_zone_table_path',
            label=u'Climate Zone Table (CSV)',
            validator=self.validator)
        self.climate_zone_container.add_input(self.climate_zone_table_path)
        self.climate_zone_raster_path = inputs.File(
            args_key=u'climate_zone_raster_path',
            helptext=(
                u"Map of climate zones that are found in the Climate "
                u"Zone Table input.  Pixel values correspond to cz_id."),
            label=u'Climate Zone (Raster)',
            validator=self.validator)
        self.climate_zone_container.add_input(self.climate_zone_raster_path)
        self.user_defined_local_recharge_container = inputs.Container(
            args_key=u'user_defined_local_recharge',
            expandable=True,
            label=u'User Defined Recharge Layer (Advanced)')
        self.add_input(self.user_defined_local_recharge_container)
        self.l_path = inputs.File(
            args_key=u'l_path',
            label=u'Local Recharge (Raster)',
            validator=self.validator)
        self.user_defined_local_recharge_container.add_input(self.l_path)
        self.monthly_alpha_container = inputs.Container(
            args_key=u'monthly_alpha',
            expandable=True,
            label=u'Monthly Alpha Table (Advanced)')
        self.add_input(self.monthly_alpha_container)
        self.monthly_alpha_path = inputs.File(
            args_key=u'monthly_alpha_path',
            label=u'Monthly Alpha Table (csv)',
            validator=self.validator)
        self.monthly_alpha_container.add_input(self.monthly_alpha_path)

        # Set interactivity, requirement as input sufficiency changes
        self.user_defined_local_recharge_container.sufficiency_changed.connect(
            self.et0_dir.set_noninteractive)
        self.user_defined_local_recharge_container.sufficiency_changed.connect(
            self.precip_dir.set_noninteractive)
        self.user_defined_local_recharge_container.sufficiency_changed.connect(
            self.soil_group_path.set_noninteractive)
        self.user_defined_local_recharge_container.sufficiency_changed.connect(
            self.rain_events_table_path.set_noninteractive)
        self.monthly_alpha_container.sufficiency_changed.connect(
            self.alpha_m.set_noninteractive)

    def assemble_args(self):
        args = {
            self.workspace.args_key: self.workspace.value(),
            self.suffix.args_key: self.suffix.value(),
            self.threshold_flow_accumulation.args_key:
                self.threshold_flow_accumulation.value(),
            self.et0_dir.args_key: self.et0_dir.value(),
            self.precip_dir.args_key: self.precip_dir.value(),
            self.dem_raster_path.args_key: self.dem_raster_path.value(),
            self.lulc_raster_path.args_key: self.lulc_raster_path.value(),
            self.soil_group_path.args_key: self.soil_group_path.value(),
            self.aoi_path.args_key: self.aoi_path.value(),
            self.biophysical_table_path.args_key:
                self.biophysical_table_path.value(),
            self.rain_events_table_path.args_key:
                self.rain_events_table_path.value(),
            self.alpha_m.args_key: self.alpha_m.value(),
            self.beta_i.args_key: self.beta_i.value(),
            self.gamma.args_key: self.gamma.value(),
            self.climate_zone_container.args_key:
                self.climate_zone_container.value(),
            self.user_defined_local_recharge_container.args_key:
                self.user_defined_local_recharge_container.value(),
            self.monthly_alpha_container.args_key:
                self.monthly_alpha_container.value(),
        }

        if self.user_defined_local_recharge_container.value():
            args[self.l_path.args_key] = self.l_path.value()

        if self.climate_zone_container.value():
            args[self.climate_zone_table_path.args_key] = (
                self.climate_zone_table_path.value())
            args[self.climate_zone_raster_path.args_key] = (
                self.climate_zone_raster_path.value())

        if self.monthly_alpha_container.value():
            args[self.monthly_alpha_path.args_key] = (
                self.monthly_alpha_path.value())

        return args