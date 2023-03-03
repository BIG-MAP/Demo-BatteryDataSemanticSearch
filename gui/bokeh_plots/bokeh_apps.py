# This module specifies classes to instantiate Bokeh apps
# using DLite objects based on the BatteryTimeSeries data model

from bokeh.io import show, save
from bokeh.layouts import row, column, Spacer
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Select, CustomJS



class AppTimeSeries:
    """
    -- Insert here final description --.

    Parameters:
        data_dict: dict
            dictionary of (col_name_string, array) pairs.
    """
    
    def __init__(self, data_object) -> None:

        self.id = ""
        self.data_object = data_object
        self.generate_data_dict()
        self.build_data_sources()
        self.create_widgets()
        self.create_plot()
        self.style_plot()
        self.attach_js_code()
        self.app = self.assemble_layout()


    def generate_data_dict(self):
        """
        To be replaced depending on the dlite object input
        """

        self.varnames = []
        self.default_x = ""
        self.default_y = ""
        self.npoints = 0
        self.data_dict = {}        



    def build_data_sources(self):

        self.full_data_source = ColumnDataSource(data=self.data_dict)

        render_data_dict = {"x":self.data_dict[self.default_x],
                             "y":self.data_dict[self.default_y]}

        self.render_data_source = ColumnDataSource(data=render_data_dict)

        

    
    def create_widgets(self):

        self.x_selector = Select(title="x", 
                                options=self.varnames, 
                                value=self.default_x, width=200)

        self.y_selector = Select(title="y", 
                                options=self.varnames, 
                                value=self.default_y, width=200)


    def create_plot(self):
        self.plot = figure(frame_height=550,
                    frame_width=550,
                    x_axis_label=self.default_x,
                    y_axis_label=self.default_y)

        self.glyph = self.plot.circle(source=self.render_data_source, 
                                    x="x", y="y")

        


    def style_plot(self):

        self.plot.toolbar.logo = None
        self.plot.xaxis.axis_label_text_font_size = "20pt"
        self.plot.yaxis.axis_label_text_font_size = "20pt"
        self.plot.xaxis.major_label_text_font_size = "15pt"
        self.plot.yaxis.major_label_text_font_size = "15pt"
        self.plot.title = self.id

        self.glyph.glyph.size = 15         
        self.glyph.glyph.fill_color="#04bfbf"
        self.glyph.glyph.line_color="#04bfbf"
        
        self.x_selector



    def attach_js_code(self):
        
        js_code = """

        render_source.data['x'] = [];
        render_source.data['y'] = [];

        for (var i = 0; i < npoints; i++) {
            
            render_source.data['x'].push(full_source.data[x_selector.value][i]);
            render_source.data['y'].push(full_source.data[y_selector.value][i]);
            
        }

        xaxis[0].axis_label = x_selector.value;
        yaxis[0].axis_label = y_selector.value;

        render_source.change.emit();

        """

        args = dict(
            npoints = self.npoints,
            full_source = self.full_data_source, 
            render_source = self.render_data_source, 
            x_selector = self.x_selector, 
            y_selector = self.y_selector,
            xaxis=self.plot.xaxis,
            yaxis=self.plot.yaxis
        )

        self.x_selector.js_on_change("value", CustomJS(code=js_code, args=args))
        self.y_selector.js_on_change("value", CustomJS(code=js_code, args=args))



    def assemble_layout(self):

        layout = row(self.plot,
                    Spacer(width=15),
                    column(self.x_selector,
                            Spacer(height=15),
                            self.y_selector),         
                    )

        return layout


    #Public methods
            
        
    def render_app(self):
        show(self.app)


    def save_app(self, path_to_save:str):
        save(self.app, path_to_save)






class InstanceApp(AppTimeSeries):
    """Takes as input a dlite_instance"""

    def __init__(self, dlite_instance, key_for_cell_id:str):
        self.cell_id_key = key_for_cell_id
        super().__init__(dlite_instance)


    def generate_data_dict(self):

        self.varnames = [key for key in self.data_object.properties.keys() if key != self.cell_id_key]
        self.id = self.data_object.properties[self.cell_id_key]

        assert len(self.varnames) > 1, "There should be at least 2 columns to plot the Time series data. Currently just found {}".format(self.varnames)

        self.default_x = self.varnames[0]
        self.default_y = self.varnames[1]
        self.npoints = self.data_object.n_measurements
        self.data_dict = self.data_object.properties

        

class DictionaryApp(AppTimeSeries):
    """Takes as input a dictionary"""

    def __init__(self, raw_data_dict:dict, dataset_id:str):
        self.id = dataset_id
        super().__init__(raw_data_dict)


    def generate_data_dict(self):

        self.varnames = list(self.data_object.keys())

        assert len(self.varnames) > 1, "There should be at least 2 columns to plot the Time series data. Currently just found {}".format(self.varnames)

        self.default_x = self.varnames[0]
        self.default_y = self.varnames[1]

        self.npoints = len(self.data_object[self.default_x])

        self.data_dict = self.data_object


def render_example_bokeh_app()-> None:
    import pandas as pd
    import os

    THISDIR = os.path.abspath('')
    URLS_CSV = "https://www.batteryarchive.org/data/CALCE_CX2-16_prism_LCO_25C_0-100_0.5-0.5C_a_timeseries.csv"

    data_dict = pd.read_csv(URLS_CSV).to_dict(orient="list")

    dict_app = DictionaryApp(data_dict, URLS_CSV.split("/")[-1])

    dict_app.render_app()


if __name__ == "__main__":
    render_example_bokeh_app()
