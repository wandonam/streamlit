class Color:
    RED = "#ff1100"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    BROWN = "#783f04"
    WHITE = "#fafafa"
    GRAY = "#d3d3d3"
    SKYBLUE = "#b3e5fc"
    

    def get_color(cls, name):
        return getattr(cls, name.upper(), none)