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

    def get_color(cls, name):
        return getattr(cls, name.upper(), none)