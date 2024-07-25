class Color:
    RED = "#ff1100"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    BROWN = "#783f04"
    WHITE = "#fafafa"
    GRAY = "#d3d3d3"
    SKYBLUE = "#b3e5fc"
    BLACK = "#262730"
    R_BLACK = "#000000"
    S_GRAY = "#bcbcbc"
    CF24 = "#fce5cd"
    SS = "#b6d7a8"
    CP = "#e07366"
    RG = "#9fc5e8"
    ETC = "#f8f2f2"

    def get_color(cls, name):
        return getattr(cls, name.upper(), None)