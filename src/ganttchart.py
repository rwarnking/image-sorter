from math import ceil
from tkinter import StringVar

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

SHOW_RESULTS = 5


class GanttChart(object):
    """
    Gantt Chart class
    Resources: TODO check again
    https://www.datacamp.com/tutorial/how-to-make-gantt-chart-in-python-matplotlib
    https://www.studytonight.com/tkinter/python-tkinter-canvas-widget
    https://www.pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/
    """

    def __init__(self, root):
        self.root = root

        self.cur_page = 1
        self.sv_gpage = StringVar()

        try:
            self.fig_p = plt.figure(1)
            self.fig_p.set_figheight(2.7)
            self.axes = plt.subplot()

            self.setup_plot()

            # Layout the plot and add it to the frame
            plt.subplots_adjust(wspace=0, hspace=0)
            plt.subplots_adjust(bottom=0.3, left=0.01, right=0.99, top=0.98)

            self.canvas = FigureCanvasTkAgg(self.fig_p, master=self.root)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="x")
        except Exception as e:
            plt.close("all")
            raise Exception(f"Creating a plot using matplotlib was unsuccessful. {e}")

    def next_page(self):
        if self.cur_page + 1 < self.max_page + 1:
            self.cur_page += 1
        self.sv_gpage.set(f"Page {self.cur_page}/{self.max_page}")
        self.update()

    def prev_page(self):
        if self.cur_page - 1 > 0:
            self.cur_page -= 1
        self.sv_gpage.set(f"Page {self.cur_page}/{self.max_page}")
        self.update()

    def set_data(self, x_min, x_max, s_dates, e_dates, y_data, lbl_data):
        assert x_min < x_max
        self.x_min = x_min
        self.x_max = x_max

        assert len(s_dates) == len(e_dates)
        assert len(s_dates) == len(y_data)
        assert len(s_dates) == len(lbl_data)
        self.s_dates = s_dates
        self.e_dates = e_dates
        self.y_data = y_data
        self.lbl_data = lbl_data

        # Update page max
        self.max_page = ceil(len(self.s_dates) / SHOW_RESULTS)
        if self.cur_page > self.max_page:
            self.cur_page = self.max_page
        self.sv_gpage.set(f"Page {self.cur_page}/{self.max_page}")

    def setup_plot(self):
        # Hide y-axis
        self.axes.get_yaxis().set_visible(False)

        # Set x-axis limits and hide the axis
        self.axes.xaxis_date()
        self.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        self.axes.tick_params("x", labelrotation=45)

    def add_bars(self):
        self.axes.set_xlim(self.x_min, self.x_max)

        margin = (self.axes.get_xbound()[1] - self.axes.get_xbound()[0]) * 0.01

        category_colors = plt.get_cmap("RdYlGn")(np.linspace(0.15, 0.85, len(self.y_data)))

        # Even though we iterate here twice, it is faster to do this, rather than unzip or append
        tmp = range(len(self.s_dates))
        indexs = [i for i in tmp]
        lengths = [(self.e_dates[i] - self.s_dates[i]) for i in tmp]

        start = (self.cur_page - 1) * SHOW_RESULTS
        end = self.cur_page * SHOW_RESULTS

        self.hbars = self.axes.barh(
            indexs[start:end],
            lengths[start:end],
            left=self.s_dates[start:end],
            align="center",
            data=self.lbl_data[start:end],
            color=category_colors[start:end],
        )

        for i, bar in enumerate(self.hbars):
            self.axes.text(
                # Put the text in the beginning of each bar using get_xbound.
                self.axes.get_xbound()[0] + margin,
                # Vertically, add the height of the bar to the start of the bar,
                # along with the offset.
                bar.get_y() + bar.get_height() * 0.5,
                # This is actual value we'll show.
                self.y_data[start:end][i],
                # Center the labels and style them a bit.
                ha="left",
                va="center",
                size=8,
            )

            self.axes.text(
                self.axes.get_xbound()[1] - margin,
                bar.get_y() + bar.get_height() * 0.5,
                self.lbl_data[start:end][i],
                ha="right",
                va="center",
                size=8,
            )

    def update(self):
        self.axes.clear()
        self.add_bars()
        self.canvas.draw()
