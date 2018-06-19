"""
Description: This module contains different functions for Bokeh server.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""

import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.io import output_file, show, save
from bokeh.sampledata.stocks import AAPL, GOOG, IBM, MSFT
from bokeh.sampledata.iris import flowers
from math import pi
from bokeh.models import HoverTool, ResetTool, PanTool, WheelPanTool, WheelZoomTool, SaveTool, ColumnDataSource
from bokeh.sampledata.periodic_table import elements
from bokeh.models.annotations import Span, BoxAnnotation, Label, LabelSet
# importing libraries
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.io import output_file, show, save
from bokeh.models.annotations import LabelSet
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.widgets import Select, TextInput, Button, Paragraph
from bokeh.models.widgets import RadioButtonGroup
from bokeh.layouts import layout
from bokeh.models.widgets import Select, Slider


class Widget:
    def __init__(self):
        self.output = None
        self.text_input = None

    def section_2_lection_44_without_server(self):
        output_file("simple_bockeh.html")
        self.text_input = TextInput(value='Input text...')
        button = Button(label='Generate Text')
        self.output=Paragraph()
        button.on_click(self.update_paragraph)
        lay_out = layout([[button, self.text_input], [self.output]])
        show(lay_out)

    def section_2_lection_44_with_server(self):
        self.text_input = TextInput(value='Input text...')
        button = Button(label='Generate Text')
        self.output=Paragraph()
        button.on_click(self.update_paragraph)
        lay_out = layout([[button, self.text_input], [self.output]])
        curdoc().add_root(lay_out)

    def update_paragraph(self):
        self.output.text = 'Hello, ' + self.text_input.value

    def select_label(self):
        source = ColumnDataSource(dict(average_grades=["B+", "A", "D-"],
                                       exam_grades=["A+", "C", "D"],
                                       student_names=["Stephan", "Helder", "Riazudidn"]))

        # create the figure
        f = figure(x_range=["F", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+"],
                   y_range=["F", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+"])

        # add labels for glyphs
        labels = LabelSet(x="average_grades", y="exam_grades", text="student_names", x_offset=5, y_offset=5,
                          source=source)
        f.add_layout(labels)

        # create glyphs
        f.circle(x="average_grades", y="exam_grades", source=source, size=8)

        # create function
        def update_labels(attr, old, new):
            labels.text = select.value

        # create select widget
        options = [("average_grades", "Average Grades"), ("exam_grades", "Exam Grades"),
                   ("student_names", "Student Names")]
        select = Select(title="Attribute", options=options)
        select.on_change("value", update_labels)

        # create layout and add to curdoc
        lay_out = layout([[select]])
        curdoc().add_root(f)
        curdoc().add_root(lay_out)

    def exercise_8_creating_span_annotations_depicting_averages(self):
        # start Bokeh server by: bokeh serve server.py
        # Remove rows with NaN values and then map standard states to colors
        elements.dropna(inplace=True)  # if inplace is not set to True the changes are not written to the dataframe
        colormap = {'gas': 'yellow', 'liquid': 'orange', 'solid': 'red'}
        elements['color'] = [colormap[x] for x in elements['standard state']]
        elements['van der Waals radius'] = elements['van der Waals radius']/10

        # Create three ColumnDataSources for elements of unique standard states
        gas = ColumnDataSource(elements[elements['standard state'] == 'gas'])
        liquid = ColumnDataSource(elements[elements['standard state'] == 'liquid'])
        solid = ColumnDataSource(elements[elements['standard state'] == 'solid'])

        # Create the figure object
        f = figure()

        # adding glyphs
        size_list = [i / 10 for i in gas.data["van der Waals radius"]]
        f.circle(x="atomic radius", y="boiling point",
                 size="van der Waals radius", fill_alpha=0.2, color="color", legend='Gas', source=gas)

        f.circle(x="atomic radius", y="boiling point",
                 size="van der Waals radius",
                 fill_alpha=0.2, color="color", legend='Liquid', source=liquid)

        f.circle(x="atomic radius", y="boiling point",
                 size="van der Waals radius",
                 fill_alpha=0.2, color="color", legend='Solid', source=solid)

        # Add axis labels
        f.xaxis.axis_label = "Atomic radius"
        f.yaxis.axis_label = "Boiling point"

        # Calculate the average boiling point for all three groups by dividing the sum by the number of values
        gas_average_boil = sum(solid.data['boiling point']) / len(solid.data['boiling point'])
        liquid_average_boil = sum(liquid.data['boiling point']) / len(liquid.data['boiling point'])
        solid_average_boil = sum(solid.data['boiling point']) / len(solid.data['boiling point'])
        solid_min_boil = min(solid.data['boiling point'])
        solid_max_boil = max(solid.data['boiling point'])

        # Create three spans
        span_gas_average_boil = Span(location=gas_average_boil, dimension='width', line_color='yellow', line_width=2)
        span_liquid_average_boil = Span(location=liquid_average_boil, dimension='width', line_color='orange',
                                        line_width=2)
        span_solid_boil = Span(location=solid_average_boil, dimension='width', line_color='red',
                               line_width=2)  # Location for this span will be updated when the Select widget is changed by the user

        # Add spans to the figure
        f.add_layout(span_gas_average_boil)
        f.add_layout(span_liquid_average_boil)
        f.add_layout(span_solid_boil)

        # Create a function that updates the location attribute value for span_solid_boil span
        # Also note that select.value returns values as strings so we need to convert the returned value to float
        def update_span(attr, old, new):
            span_solid_boil.location = float(select.value)

        # Select widgets expect a list of tuples of strings, so List[Tuple(String, String)], that's why you should convert average, max, and min to strings
        options = [(str(solid_average_boil), "Solid Average Boiling Point"),
                   (str(solid_min_boil), "Solid Minimum Boiling Point"),
                   (str(solid_max_boil), "Solid Maximum Boiling Point")]

        # Create the Select widget
        select = Select(title="Select span value", options=options)
        select.on_change("value", update_span)

        # Add Select widget to layout and then the layout to curdoc
        lay_out = layout([[select]])
        curdoc().add_root(f)
        curdoc().add_root(lay_out)

    def use_server_with_radio_buttons(self):
        # crate columndatasource
        source = ColumnDataSource(dict(average_grades=["B+", "A", "D-"],
                                       exam_grades=["A+", "C", "D"],
                                       student_names=["Stephan", "Helder", "Riazudidn"]))

        # create the figure
        f = figure(x_range=["F", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+"],
                   y_range=["F", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+"])

        # add labels for glyphs
        labels = LabelSet(x="average_grades", y="exam_grades", text="student_names", x_offset=5, y_offset=5,
                          source=source)
        f.add_layout(labels)

        # create glyphs
        f.circle(x="average_grades", y="exam_grades", source=source, size=8)

        # create function
        def update_labels(attr, old, new):
            labels.text = options[radio_button_group.active]

        # create select widget
        options = ["average_grades", "exam_grades", "student_names"]
        radio_button_group = RadioButtonGroup(labels=options)
        radio_button_group.on_change("active", update_labels)

        # create layout and add to curdoc
        lay_out = layout([[radio_button_group]])
        curdoc().add_root(f)
        curdoc().add_root(lay_out)

    def use_server_to_change_glyphs(self):
        source_original = ColumnDataSource(dict(average_grades=[7, 8, 10],
                                                exam_grades=[6, 9, 8],
                                                student_names=["Stephan", "Helder", "Riazudidn"]))

        source = ColumnDataSource(dict(average_grades=[7, 8, 10],
                                       exam_grades=[6, 9, 8],
                                       student_names=["Stephan", "Helder", "Riazudidn"]))

        # create the figure
        f = figure(x_range=Range1d(start=0, end=12),
                   y_range=Range1d(start=0, end=12))

        # add labels for glyphs
        labels = LabelSet(x="average_grades", y="exam_grades", text="student_names", x_offset=5, y_offset=5,
                          source=source)
        f.add_layout(labels)

        # create glyphs
        f.circle(x="average_grades", y="exam_grades", source=source, size=8)

        # create filtering function
        def filter_grades(attr, old, new):
            source.data = {key: [value for i, value in enumerate(source_original.data[key]) if
                                 source_original.data["exam_grades"][i] >= slider.value] for key in
                           source_original.data}
            print(slider.value)

        # create label function
        def update_labels(attr, old, new):
            labels.text = select.value

        # create select widget
        options = [("average_grades", "Average Grades"), ("exam_grades", "Exam Grades"),
                   ("student_names", "Student Names")]
        select = Select(title="Attribute", options=options)
        select.on_change("value", update_labels)

        slider = Slider(start=min(source_original.data["exam_grades"]) - 1,
                        end=max(source_original.data["exam_grades"]) + 1, value=8, step=0.1, title="Exam Grade: ")
        slider.on_change("value", filter_grades)

        # create layout and add to curdoc
        lay_out = layout([[select], [slider]])
        curdoc().add_root(f)
        curdoc().add_root(lay_out)


widget = Widget()
widget.use_server_to_change_glyphs()