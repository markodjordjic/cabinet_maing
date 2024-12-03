import matplotlib.pyplot as plt
import matplotlib.gridspec as grid
from matplotlib.patches import Rectangle

inch_in_mm = 25.4
paper_height = 11.69
paper_width = 8.27
height_mm = 2304
depth_mm = 540 
height_inch = height_mm / inch_in_mm
depth_inch = depth_mm / inch_in_mm
coefficient = 10
scaled_height = height_inch / coefficient
scaled_width = depth_inch / coefficient
cabinet_relative_height = scaled_height / paper_height
cabinet_relative_depth = scaled_width / paper_width
shelve_clearance_in = 12 / inch_in_mm / coefficient / paper_height 
height_from_center = .5 - (cabinet_relative_height/2)
depth_from_center = .5 - (cabinet_relative_depth/2)
panel_thickness = 18 / inch_in_mm / coefficient / paper_height
rail = 96 / inch_in_mm / coefficient / paper_height
cabinet_top = (cabinet_relative_height/2) + 0.5
mm_6 = 6 / inch_in_mm / coefficient / paper_height
mm_3 = 3 / inch_in_mm / coefficient / paper_height
shelves = [
    2144, 1984, 1824, 1440, 1280, 1120, 960, 800, 480, 320, 160       
]

shelves_in_inch = [
    position/inch_in_mm for position in shelves
]

def compute_drawing_position(real_position: int = None):
    scaled_position = real_position / coefficient
    relative_scaled_position = scaled_position / paper_height
    from_center = (.5+(cabinet_relative_height/2)) - relative_scaled_position
    # if relative_scaled_position < .5:
    #     from_center = .5 + (cabinet_relative_depth/2)
    # if relative_scaled_position >= .5:
    #     from_center = .5 - (cabinet_relative_depth/2)

    return from_center, depth_from_center


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
# Bottom.
axis_1.add_patch(
    Rectangle(
        xy=(depth_from_center, height_from_center),
        width=cabinet_relative_depth,
        height=panel_thickness,
        fill=True
    )
)
# Top.
axis_1.add_patch(
    Rectangle(
        xy=(depth_from_center, (cabinet_top - panel_thickness)),
        width=cabinet_relative_depth,
        height=panel_thickness,
        fill=False
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
        fill=False
    )
)
# Shelves.
for shelve in shelves_in_inch:
    x, y = compute_drawing_position(shelve)
    print(x, y)
    axis_1.add_patch(Rectangle(
        xy=(y+mm_6, 1-x), 
        width=cabinet_relative_depth - shelve_clearance_in, 
        height=panel_thickness, 
        fill=False
    ))
# Back.
axis_1.add_patch(Rectangle(
    xy=(depth_from_center + mm_3, height_from_center + mm_6),
    width=mm_3,
    height=cabinet_relative_height - (2*mm_6),
    fill=False
))
axis_1.tick_params(labeltop=True, labelright=True)
axis_1.tick_params(axis='both', direction='in')
axis_1.tick_params(bottom=True, top=True, left=True, right=True) 
axis_1.set_xticklabels([])
axis_1.set_yticklabels([])
figure.subplots_adjust(left=.25, right=.75)
plt.show()
