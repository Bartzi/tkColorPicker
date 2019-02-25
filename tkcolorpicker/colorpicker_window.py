import tkinter as tk
from collections import OrderedDict

from libs.tkColorPicker.tkcolorpicker.colorchooser import _, ColorChooser
from libs.tkColorPicker.tkcolorpicker.colorsquare import ColorSquare
from libs.tkColorPicker.tkcolorpicker.functions import rgb_to_hsv
from libs.tkColorPicker.tkcolorpicker.limitvar import MaxValueVar
from libs.tkColorPicker.tkcolorpicker.tolerance_chooser import ToleranceChooser


class ColorPicker(tk.Toplevel):

    def __init__(self, parent=None, color=(255, 0, 0), title=_("Color Chooser")):
        super().__init__(parent)

        self.title(title)
        self.transient(self.master)
        self.resizable(False, False)

        self.color = color

        self.create_color_chooser(color)

        tolerance_frame = self.creat_tolerance_chooser()
        self.create_buttons(tolerance_frame)

        self.create_included_colors_viewer()

        self.wait_visibility()
        self.lift()
        self.grab_set()

    def create_included_colors_viewer(self):
        included_colors_area = tk.LabelFrame(self, text=_("Included Colors"))
        included_colors_area.grid(row=0, column=2, stick='n')
        use_saturation_for_y = tk.BooleanVar(self, value=True)
        button_frame = tk.Frame(included_colors_area)
        tk.Grid.rowconfigure(button_frame, 0, weight=1)
        tk.Grid.columnconfigure(button_frame, 0, weight=1)
        hue_and_saturation = tk.Radiobutton(button_frame, text="hue and saturation", variable=use_saturation_for_y,
                                            value=True)
        hue_and_saturation.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W)
        hue_and_saturation.bind("<ButtonRelease-1>", lambda e: self.event_generate("<<Redraw>>"))
        hue_and_value = tk.Radiobutton(button_frame, text="hue and value", variable=use_saturation_for_y, value=False)
        hue_and_value.grid(row=0, column=1, sticky=tk.N + tk.S + tk.E + tk.W)
        hue_and_value.bind("<ButtonRelease-1>", lambda e: self.event_generate("<<Redraw>>"))
        button_frame.pack(fill='both', anchor=tk.N)
        self.color_square = ColorSquare(included_colors_area, self.color_components, self.tolerance_components,
                                        include_saturation=use_saturation_for_y)
        self.color_square.pack(anchor=tk.S)
        self.bind("<<Redraw>>", lambda e: self.color_square.fill_square())

    def create_buttons(self, tolerance_frame):
        button_frame = tk.Frame(tolerance_frame)
        button_frame.pack(side='bottom', pady=20)
        for text in ["Ok", "Cancel"]:
            tk.Button(button_frame, text=_(text), command=self.ok).pack(side='right', padx=10, ipadx=20, ipady=20)

    def creat_tolerance_chooser(self):
        tolerance_frame = tk.Frame(self, padx=15)
        tolerance_frame.grid(row=0, column=1, stick='n')
        self.hue_tolerance = MaxValueVar(tolerance_frame, 0, max_value=100, name='hue_tolerance')
        self.saturation_tolerance = MaxValueVar(tolerance_frame, 0, max_value=100, name='saturation_tolerance')
        self.value_tolerance = MaxValueVar(tolerance_frame, 0, max_value=100, name='value_tolerance')
        self.tolerance_components = OrderedDict({
            "hue": self.hue_tolerance,
            "saturation": self.saturation_tolerance,
            "value": self.value_tolerance,
        })
        tolerance_label = tk.LabelFrame(tolerance_frame, text=_("Tolerance in %"))
        tolerance_label.pack()
        self.tolerance_chooser = ToleranceChooser(tolerance_label, self.tolerance_components)
        # self.tolerance_chooser.bind('<Button-1>', test)
        self.tolerance_chooser.grid(row=1, column=1)
        return tolerance_frame

    def create_color_chooser(self, color):
        h, s, v = rgb_to_hsv(*color)
        self.hue = MaxValueVar(self, h, max_value=360, name='hue')
        self.saturation = MaxValueVar(self, s, max_value=100, name='saturation')
        self.value = MaxValueVar(self, v, max_value=100, name='value')
        self.color_components = OrderedDict({
            "hue": self.hue,
            "saturation": self.saturation,
            "value": self.value,
        })
        color_frame = tk.Frame(self)
        color_frame.grid(row=0, column=0, stick='n')
        color_label = tk.LabelFrame(color_frame, text=_("Color"))
        color_label.pack()

        self.color_chooser = ColorChooser(color_label, self.color_components)
        self.color_chooser.grid(row=0, column=0)

    def get_result(self):
        return {
            "color": [color_component.get() for color_component in self.color_components.values()],
            "tolerances": [tolerance_component.get() for tolerance_component in self.tolerance_components.values()]
        }

    def reset(self):
        h, s, v = rgb_to_hsv(*self.color)
        self.hue.set(h)
        self.saturation.set(s)
        self.value.set(v)

        for tolerance_component in self.tolerance_components.values():
            tolerance_component.set(0)

    def ok(self):
        """
            destroy the dialog in order to return to calling code
        """
        self.destroy()
        for var in [self.hue, self.saturation, self.value]:
            tracers = var.trace_info()
            for trace_type, callback_name in tracers:
                var.trace_remove(trace_type, callback_name)

    def cancel(self):
        """
            restore startup color and tolerances and set it as color that will be read by code that called this dialog
        """
        self.reset()
        self.destroy()


def askcolor(color=(255, 0, 0), parent=None, title=_("Color Chooser")):
    """
    Open a ColorPicker dialog and return the chosen color.

    The selected color is retunred in HSV format.
    (None, None) is returned if the color selection is cancelled.

    Arguments:
        * color: initially selected color (RGB(A), hexa or tkinter color name)
        * parent: parent window
        * title: dialog title
        * alpha: alpha channel suppport
    """
    picker = ColorPicker(parent, color, title)
    picker.wait_window(picker)
    res = picker.get_result()
    return res

