from itertools import chain
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid
from matplotlib.patches import Rectangle, Circle

horizontal_reference = .33
inch_in_mm = 25.4
paper_height = 11.69
paper_width = 8.27
height_mm = 2304
depth_mm = 540
width_mm = 540 
height_inch = height_mm / inch_in_mm
depth_inch = depth_mm / inch_in_mm
width_inch = width_mm / inch_in_mm
coefficient = 10
scaled_height = height_inch / coefficient
scaled_depth = depth_inch / coefficient
scaled_width = width_inch / coefficient
cabinet_relative_height = scaled_height / paper_height
cabinet_relative_depth = scaled_depth / paper_width
cabinet_relative_width = scaled_width / paper_width
shelve_clearance_in = 12 / inch_in_mm / coefficient / paper_height 
height_from_center = .5 - (cabinet_relative_height/2)
depth_from_center = horizontal_reference - (cabinet_relative_depth/2)
panel_thickness = 18 / inch_in_mm / coefficient / paper_height
rail = 96 / inch_in_mm / coefficient / paper_height
cabinet_top = (cabinet_relative_height/2) + .5
cabinet_bottom = .5 - (cabinet_relative_height/2)
mm_6 = 6 / inch_in_mm / coefficient / paper_height
mm_5 = 5 / inch_in_mm / coefficient / paper_height
mm_3 = 3 / inch_in_mm / coefficient / paper_height
mm_37 = 37 / inch_in_mm / coefficient / paper_height

shelves = [
    2144, 1984, 1824, 1440, 1280, 1120, 960, 800, 480, 320, 160       
]
sections = [640, 1664]

shelves_in_inch = [
    position/inch_in_mm for position in shelves
]
sections_in_inch = [
    position/inch_in_mm for position in sections[::-1] # Reverse.
]

def compute_drawing_position(real_position: int = None):
    scaled_position = real_position / coefficient
    relative_scaled_position = scaled_position / paper_height
    from_center = (.5+(cabinet_relative_height/2)) - relative_scaled_position

    return from_center, depth_from_center


def compute_drawing_positions(real_positions: list[int] = None):
    drawing_positions = []
    for real_position in real_positions:
        drawing_position = compute_drawing_position(real_position=real_position)
        drawing_positions.append(drawing_position)
    
    return drawing_positions

def compute_drawing_positions_from_pairs(real_positions: list[list[float]] = None):
    drawing_positions = []
    for pair in real_positions:
        drawing_position_per_pair = []
        for component in pair:
            drawing_position = compute_drawing_position(real_position=component)
            drawing_position_per_pair.append(drawing_position)
        drawing_positions.append(drawing_position_per_pair)
    
    return drawing_positions


def indicate_sections(sections):
    # Section starts, and section ends.
    zero_padding = [0] + sections        
    cumulative_heights = np.cumsum(zero_padding)
    pairs = [
        [height_inch-cumulative_heights[i], height_inch-cumulative_heights[i + 1]]
        for i in range(len(cumulative_heights) - 1)
    ]

    return pairs

section_pairs = indicate_sections(sections=sections_in_inch)

section_positions = compute_drawing_positions_from_pairs(
    section_pairs
)

plt.rcParams["font.size"] = 8
# Set figure size
figure = plt.figure(figsize=(8.27, 11.69))
plotting_grid = grid.GridSpec(nrows=1, ncols=1)
axis_1 = figure.add_subplot(plotting_grid[0, 0])
# Box.
axis_1.add_patch(
    Rectangle(
        xy=(depth_from_center, height_from_center), 
        width=cabinet_relative_depth, 
        height=cabinet_relative_height, 
        fill=False
    )
)
# System holes.
system_holes_positions = [
    height_mm-2240,
    height_mm-2208,
    height_mm-1760,
    height_mm-1728,
    height_mm-1600,
    height_mm-1568,
    height_mm-96,
    height_mm-64
]
system_holes_labels = ['S1H1B', 'S1H1T', 'S1H2B', 'S1H2T', 'S2H1B', 'S2H1T', 'S2H2B', 'S2H2T']
for index, position in enumerate(system_holes_positions):
    axis_1.add_patch(
        Circle(xy=(
            depth_from_center
            + cabinet_relative_depth
            - mm_37, 
            (.5+(cabinet_relative_height/2))-(position/inch_in_mm/coefficient/paper_height)
        ), radius=mm_5)
    )
    plt.pause(2)
# Bottom.
axis_1.add_patch(
    Rectangle(
        xy=(depth_from_center, height_from_center),
        width=cabinet_relative_depth,
        height=panel_thickness,
        fill=False,
        hatch='/////'
    )
)
axis_1.add_patch(
    Rectangle(
        xy=(
            depth_from_center + mm_6,
            (
                cabinet_bottom
                + panel_thickness
            )
        ),
        width=panel_thickness,
        height=rail,
        fill=False,
        hatch='/////'
    )
)
# Top.
axis_1.add_patch(
    Rectangle(
        xy=(depth_from_center, (cabinet_top - panel_thickness)),
        width=cabinet_relative_depth,
        height=panel_thickness,
        fill=False,
        hatch='/////'
    )
)
axis_1.add_patch(
    Rectangle(
        xy=(
            depth_from_center + mm_6,
            (
                cabinet_top
                - panel_thickness
                - rail
            )
        ),
        width=panel_thickness,
        height=rail,
        fill=False,
        hatch='/////'
    )
)
# Back.
axis_1.add_patch(Rectangle(
    xy=(depth_from_center + mm_3, height_from_center + mm_6),
    width=mm_3,
    height=cabinet_relative_height - (2*mm_6),
    fill=True,
    facecolor='k'
))
# Empty between the back and the wall.
axis_1.add_patch(Rectangle(
    xy=(depth_from_center, height_from_center + mm_6),
    width=mm_3,
    height=cabinet_relative_height - (2*mm_6),
    fill=True,
    facecolor='white',
    edgecolor=None
))
# Shelves.
for shelve in shelves_in_inch:
    x, y = compute_drawing_position(shelve)
    axis_1.add_patch(Rectangle(
        xy=(y+mm_6, 1-x), 
        width=cabinet_relative_depth - shelve_clearance_in, 
        height=panel_thickness, 
        fill=False,
        linestyle='--'
    ))
# Elevation.
# Box.
axis_1.add_patch(
    Rectangle(
        xy=(1 - depth_from_center*2, height_from_center), 
        width=cabinet_relative_width, 
        height=cabinet_relative_height, 
        fill=True,
        facecolor='k'
    )
)
# Sections.
for index, section_pair in enumerate(section_positions):
    axis_1.add_patch(
        Rectangle(
            xy=((1 - depth_from_center*2)+(mm_3*.5), section_pair[0][0]+(mm_3*.5)), 
            width=cabinet_relative_width - mm_3,  # Compensate for being pushed.
            height=(sections_in_inch[index]/coefficient/paper_height)-(mm_3), 
            fill=True,
            facecolor='lightgray',
        )
    )
axis_1.tick_params(labeltop=True, labelright=True)
axis_1.tick_params(axis='both', direction='in')
axis_1.tick_params(bottom=True, top=True, left=True, right=True) 
axis_1.set_xticklabels([])
axis_1.set_yticklabels([])
#figure.subplots_adjust(left=.25, right=.75)
plt.tight_layout()
plt.savefig(fname='cabinet.pdf', dpi=1200, format='pdf')
plt.show()
