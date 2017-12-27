import matplotlib as mpl


def mpl_setup(scale=0.49, aspect_ratio=8.0 / 6.0,
              pad_left=0.16, pad_bottom=0.18,
              pad_right=0.95, pad_top=0.95):
    mpl.rcParams["font.sans-serif"] = ["Liberation Sans", "helvetica",
                                       "Helvetica", "Arial"]
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.size"] = 8
    mpl.rcParams["mathtext.default"] = "regular"

    # LaTeX \the\textwidth
    text_width_pt = 451.58598
    inches_per_pt = 1.0 / 72.27
    fig_width = text_width_pt * inches_per_pt * scale
    fig_height = fig_width / aspect_ratio

    mpl.rcParams["figure.figsize"] = [fig_width, fig_height]

    mpl.rcParams["figure.subplot.left"] = pad_left
    mpl.rcParams["figure.subplot.bottom"] = pad_bottom
    mpl.rcParams["figure.subplot.top"] = pad_top
    mpl.rcParams["figure.subplot.right"] = pad_right

    mpl.rcParams["axes.xmargin"] = 0.0
    mpl.rcParams["axes.ymargin"] = 0.0

    mpl.rcParams["axes.labelsize"] = 10
    mpl.rcParams["axes.linewidth"] = 0.6

    mpl.rcParams["xtick.major.size"] = 6.0
    mpl.rcParams["xtick.major.width"] = 0.6
    mpl.rcParams["xtick.minor.size"] = 3.0
    mpl.rcParams["xtick.minor.width"] = 0.6
    mpl.rcParams["xtick.minor.visible"] = True
    mpl.rcParams["xtick.top"] = True
    mpl.rcParams["xtick.direction"] = "in"
    mpl.rcParams["xtick.labelsize"] = 8

    mpl.rcParams["ytick.major.size"] = 6.0
    mpl.rcParams["ytick.major.width"] = 0.6
    mpl.rcParams["ytick.minor.size"] = 3.0
    mpl.rcParams["ytick.minor.width"] = 0.6
    mpl.rcParams["ytick.minor.visible"] = True
    mpl.rcParams["ytick.right"] = True
    mpl.rcParams["ytick.direction"] = "in"
    mpl.rcParams["ytick.labelsize"] = 8

    mpl.rcParams["legend.frameon"] = False

    mpl.rcParams["lines.linewidth"] = 1.1
    mpl.rcParams["lines.markersize"] = 3.0
