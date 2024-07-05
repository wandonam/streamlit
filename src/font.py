# LIBRARY
import os
import pandas as pd
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

## FONT
## Define Font
def extract_font_name(font_path):
    font_name = os.path.basename(font_path).split('.')[0]
    return font_name

def get_font_path_by_name(font_name, df_fonts):
    if font_name in df_fonts['Font Name'].values:
        return df_fonts.loc[df_fonts['Font Name'] == font_name, 'Font Path'].values[0]
    else:
        return "Font name not found"
    
## Get list
font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')

## DataFrame
font_data = []
for font_path in font_list:
    font_name = extract_font_name(font_path)
    font_data.append([font_name, font_path])

df_fonts = pd.DataFrame(font_data, columns=['Font Name', 'Font Path'])

## usage
def set_font(font_name_input):
    font_path = get_font_path_by_name(font_name_input, df_fonts)

    if font_path:
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        return True
    else:
        return False