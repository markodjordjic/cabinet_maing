import matplotlib.pyplot as plt
import matplotlib.gridspec as grid
from matplotlib.patches import Rectangle, Circle
from cabinet_making.base_classes import BaseElevation


class CabinetPlotter(BaseElevation):

    inch_in_mm = 25.4
    paper_height = 11.69
    paper_width = 8.27
    horizontal_reference = .33
    coefficient = 15
    shelve_clearance_in = None 
    panel_thickness = None
    mm_37 = None
    mm_32 = None
    mm_6 = None
    mm_5 = None
    mm_3 = None
    rail = None

    def __init__(self,
                 cabinet_type: str = 'floor',
                 orientation: str = 'portrait',
                 height: int = None, 
                 depth: int = None, 
                 width: int = None,
                 dividers: list[int] = None,
                 shelves: list[int] = None,
                 drawers: list[int] = None,
                 drawer_front: list[int] = None,
                 sections: list[int] = None,
                 doors_per_section: list[int] = None,
                 section_pairs: list[int] = None,
                 system_holes: list[int] = None) -> None:
        super().__init__(height, sections, drawers, dividers, shelves)
        self.cabinet_type = cabinet_type
        self.orientation = orientation
        self.depth_mm = depth
        self.width_mm = width
        self.drawer_front = drawer_front
        self.sections = sections
        self.doors_per_section = doors_per_section
        self.height_inch = None
        self.depth_inch = None
        self.width_inch = None
        self.scaled_height = None
        self.scaled_depth = None
        self.scaled_width = None
        self.cabinet_relative_height = None
        self.cabinet_relative_depth = None
        self.cabinet_relative_width = None
        self.depth_from_center = None
        self.cabinet_top = None
        self.cabinet_bottom = None
        self.dividers_in = None
        self.shelves_in_inch = None
        self.drawers_in = None
        self.sections_in = None
        self.section_pairs_in = None
        self.section_pairs = section_pairs
        self.section_positions = None
        self.system_holes = system_holes
        self.section_pairs_positions = None

    def _set_orientation(self):
        if self.orientation == 'portrait':
            self.paper_height = 11.69
            self.paper_width = 8.27
        else:
            self.paper_height = 8.27
            self.paper_width = 11.69

    def _to_unit(self, original_measurement: int = None) -> float:
        
        return \
            original_measurement / self.inch_in_mm / self.coefficient / self.paper_height

    def _basic_computations(self):

        self.shelve_clearance_in = self._to_unit(12) # Front 6 mm, back 6 mm.
        self.panel_thickness = self._to_unit(18)
        self.mm_37 = self._to_unit(37)
        self.mm_32 = self._to_unit(32) 
        self.mm_6 = self._to_unit(6)
        self.mm_5 = self._to_unit(5)
        self.mm_3 = self._to_unit(3) 
        self.rail = self._to_unit(96)

    def compute_dimensions_in_inches(self):
        self.height_inch = self._to_inches(self.height)
        self.depth_inch = self._to_inches(self.depth_mm)
        self.width_inch = self._to_inches(self.width_mm)
        # Non mandatory elements.
        if self.dividers:
            self.dividers_in = self._to_inches(millimeters=self.dividers)
        if self.shelves:
            self.shelves_in_inch = self._to_inches(millimeters=self.shelves)
        if len(self.drawers['positions'])> 0:
            self.drawers_in = self._to_inches(millimeters=self.drawers['positions'])
        if self.sections:
            self.sections_in = self._to_inches(millimeters=self.sections)

    def compute_scaled_dimensions(self):
        self.scaled_height = self.height_inch / self.coefficient
        self.scaled_depth = self.depth_inch / self.coefficient
        self.scaled_width = self.width_inch / self.coefficient

    def compute_relative_dimensions(self):
        self.cabinet_relative_height = self.scaled_height / self.paper_height
        self.cabinet_relative_depth = self.scaled_depth / self.paper_height
        self.cabinet_relative_width = self.scaled_width / self.paper_height

    def compute_reference_dimensions(self):
        self.depth_from_center = \
            self.horizontal_reference - (self.cabinet_relative_depth/2)
        self.cabinet_top = .5 + (self.cabinet_relative_height/2)
        self.cabinet_bottom = .5 - (self.cabinet_relative_height/2)

    def _to_inches(self, millimeters: list | int = None) -> list | int:
        """Conversion of measurements

        Original measurements in millimeters are converted to inches.
        Method can accept `list` or `integer` objects and returns the
        object of the same class as the input.

        Parameters
        ----------
        millimeters : list | int, optional
            Original measurements in millimeters, by default None.

        Returns
        -------
        list | int
            Measurements in inches.

        """
        assert millimeters, 'No measurements provided.'

        if isinstance(millimeters, list):     
            output = [mm / self.inch_in_mm for mm in millimeters]
        else:
            output = millimeters / self.inch_in_mm

        return output

    def _compute_drawing_position(self, real_position: int = None) -> tuple:
        scaled_position = real_position / self.coefficient
        relative_scaled_position = scaled_position / self.paper_height
        from_center = \
            self.cabinet_bottom + relative_scaled_position

        return from_center, self.depth_from_center

    def compute_drawing_positions(self, real_positions: list[int] = None):
        drawing_positions = []
        for real_position in real_positions:
            drawing_position = self._compute_drawing_position(
                real_position=real_position
            )
            drawing_positions.append(drawing_position)
        
        return drawing_positions

    def compute_section_drawing_positions(self) -> None:
        self.section_pairs_in = \
            [self._to_inches(section) for section in self.section_pairs]
        drawing_positions = []
        for pair in self.section_pairs_in:
            drawing_position_per_pair = []
            for component in pair:
                drawing_position = \
                    self._compute_drawing_position(real_position=component)
                drawing_position_per_pair.append(drawing_position)
            drawing_positions.append(drawing_position_per_pair)
        
        self.section_pairs_positions = drawing_positions
     
    def plot_cabinet(self, 
                     compute_only: bool = False, 
                     plot_file: str = None) -> None:
        self._set_orientation()
        self._basic_computations()
        self.compute_dimensions_in_inches()
        self.compute_scaled_dimensions()
        self.compute_relative_dimensions()
        self.compute_reference_dimensions()
        if self.sections:
            self.compute_section_drawing_positions()
        plt.rcParams["font.size"] = 8
        # Set figure size
        if compute_only:
            with plt.ioff():
                figure = plt.figure(figsize=(self.paper_width, self.paper_height))
        else:
            figure = plt.figure(figsize=(self.paper_width, self.paper_height))
        plotting_grid = grid.GridSpec(nrows=1, ncols=1)
        axis_1 = figure.add_subplot(plotting_grid[0, 0])
        # Box.
        axis_1.add_patch(
            Rectangle(
                xy=(self.depth_from_center, self.cabinet_bottom), 
                width=self.cabinet_relative_depth, 
                height=self.cabinet_relative_height, 
                fill=False
            )
        )
        # System holes.
        for index, position in enumerate(self.system_holes['positions']):
            x = self.depth_from_center + self.cabinet_relative_depth - self.mm_37
            y = self.cabinet_bottom + self._to_unit(position)
            axis_1.add_patch(Circle(xy=(x, y), radius=self.mm_5))
            if 'hinge' not in self.system_holes['labels'][index]:
                x = self.depth_from_center + self.cabinet_relative_depth - self.mm_37 - (((self.depth_mm/32)-4) * self.mm_32) 
                axis_1.add_patch(Circle(xy=(x, y), radius=self.mm_5))
        # Bottom.
        axis_1.add_patch(
            Rectangle(
                xy=(self.depth_from_center, self.cabinet_bottom),
                width=self.cabinet_relative_depth,
                height=self.panel_thickness,
                fill=False,
                hatch='/////'
            )
        )
        # Bottom nailer.
        axis_1.add_patch(
            Rectangle(
                xy=(
                    self.depth_from_center + self.mm_6,
                    self.cabinet_bottom + self.panel_thickness
                ),
                width=self.panel_thickness,
                height=self.rail,
                fill=False,
                hatch='/////'
            )
        )
        # Top.
        if (self.cabinet_type == 'wall') or (self.cabinet_type == 'cupboard'):
            axis_1.add_patch(
                Rectangle(
                    xy=(
                        self.depth_from_center, 
                        (self.cabinet_top - self.panel_thickness)
                    ),
                    width=self.cabinet_relative_depth,
                    height=self.panel_thickness,
                    fill=False,
                    hatch='/////'
                )
            )
        if self.cabinet_type == 'floor':
            axis_1.add_patch(
                Rectangle(
                    xy=(
                        self.depth_from_center, 
                        (self.cabinet_top - self.panel_thickness)
                    ),
                    width=self.rail,
                    height=self.panel_thickness,
                    fill=False,
                    hatch='/////'
                )
            )
            axis_1.add_patch(
                Rectangle(
                    xy=(
                        self.depth_from_center+(self.cabinet_relative_depth)-self.rail, 
                        (self.cabinet_top - self.panel_thickness)
                    ),
                    width=self.rail,
                    height=self.panel_thickness,
                    fill=False,
                    hatch='/////'
                )
            )
        # Top nailer.
        axis_1.add_patch(
            Rectangle(
                xy=(
                    self.depth_from_center + self.mm_6,
                    (
                        self.cabinet_top
                        - self.panel_thickness
                        - self.rail
                    )
                ),
                width=self.panel_thickness,
                height=self.rail,
                fill=False,
                hatch='/////'
            )
        )
        # Back.
        axis_1.add_patch(Rectangle(
            xy=(
                self.depth_from_center + self.mm_3, 
                self.cabinet_bottom + self.mm_6
            ),
            width=self.mm_3,
            height=self.cabinet_relative_height - (2*self.mm_6),
            fill=True,
            facecolor='k'
        ))
        # Empty between the back and the wall.
        axis_1.add_patch(Rectangle(
            xy=(
                self.depth_from_center, 
                self.cabinet_bottom + self.mm_6
            ),
            width=self.mm_3,
            height=self.cabinet_relative_height - (2*self.mm_6),
            fill=True,
            facecolor='white',
            edgecolor=None
        ))
        # Dividers.
        if self.dividers_in:
            for divider in self.dividers_in:
                x, y = self._compute_drawing_position(divider)
                axis_1.add_patch(Rectangle(
                    xy=(y+self.mm_6, 1-x), 
                    width=self.cabinet_relative_depth - self.mm_6, 
                    height=self.panel_thickness, 
                    fill=False,
                    hatch='/////'
                ))      
                axis_1.add_patch(
                    Rectangle(
                        xy=(
                            y + self.mm_6,
                            1 - x - self.rail
                        ),
                        width=self.panel_thickness,
                        height=self.rail,
                        fill=False,
                        hatch='/////'
                    )
                )  
        # Shelves.
        if self.shelves:
            for shelve in self.shelves_in_inch:
                x, y = self._compute_drawing_position(shelve)
                axis_1.add_patch(Rectangle(
                    xy=(y+self.mm_6, 1-x), 
                    width=self.cabinet_relative_depth - self.shelve_clearance_in, 
                    height=self.panel_thickness, 
                    fill=False,
                    linestyle='--'
                ))
        # Drawers.
        if len(self.drawers['positions']) > 0:
            for index, drawer in enumerate(self.drawers_in[::-1]):
                x, y = self._compute_drawing_position(drawer)
                drawer_front = self._to_unit(self.drawer_front[index])
                drawer_box = drawer_front - (8*self.mm_6)
                compensation = 0
                if 'shifted' in self.drawers['registration'][::-1][index]:
                    compensation = self.mm_32 * .5
                # Box.
                axis_1.add_patch(Rectangle(
                    xy=(
                        y + (10*self.mm_5), 
                        x - (drawer_box*.5) - compensation
                    ), 
                    width=self.cabinet_relative_depth - (10*self.mm_5), 
                    height=drawer_box,
                    fill=False
                ))
                # Drawer rail.
                axis_1.add_patch(Rectangle(
                    xy=(
                        self.horizontal_reference + (self.cabinet_relative_depth/2) - self.rail, 
                        x - (drawer_box*.5) - compensation - (self.mm_32)
                    ), 
                    width=self.rail, 
                    height=self.panel_thickness,
                    fill=False,
                    hatch='/////'
                ))                
        # Elevation, box.
        horizontal_offset = \
            1 - self.horizontal_reference - (self.cabinet_relative_width/2)
        axis_1.add_patch(
            Rectangle(
                xy=(horizontal_offset, self.cabinet_bottom), 
                width=self.cabinet_relative_width, 
                height=self.cabinet_relative_height, 
                fill=True,
                facecolor='k'
            )
        )
        # Elevation, doors.
        if self.section_pairs_positions and self.doors_per_section:
            assert len(self.section_pairs) == len(self.doors_per_section), \
                'Section count and doors per section count do not match.'
            for index, section_pair in enumerate(self.section_pairs_positions):
                doors_per_section = self.doors_per_section[index]
                if doors_per_section == 0:
                    # Section with no doors.
                    pass                               
                if doors_per_section >= 1:
                    # Section with at least one door.
                    width = \
                        (self.cabinet_relative_width/doors_per_section) - self.mm_3
                    for door in range(0, doors_per_section):
                        door_compensation = 0
                        if door > 0:
                            door_compensation = self.mm_3
                        axis_1.add_patch(
                            Rectangle(
                                xy=(
                                    horizontal_offset + (self.mm_3*.5) + door*width + door_compensation, 
                                    1 - section_pair[1][0] + (self.mm_3*.5)
                                ), 
                                width=width,
                                height=(
                                    self._to_unit(self.sections[index])
                                ) - (self.mm_3), 
                                fill=True,
                                facecolor='lightgray',
                            )
                        )
        # Drawers.
        if self.drawers_in:
            for index, drawer in enumerate(self.drawers_in[::-1]):
                x, y = self._compute_drawing_position(drawer)
                axis_1.add_patch(
                    Rectangle(
                        xy=(
                            horizontal_offset+(self.mm_3*.5), 
                            x - (self._to_unit(self.drawer_front[index]*.5))
                        ), 
                        width=self.cabinet_relative_width - self.mm_3,  # Compensate for being pushed.
                        height=(
                            self._to_unit(self.drawer_front[index])
                        ) - (self.mm_3), 
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
        plt.savefig(fname=plot_file, dpi=1200, format='pdf')
        plt.close('all')


class SectionPlotter:

    inch_in_mm = 25.4
    paper_height = 8.27
    paper_width = 11.69
    horizontal_reference = .1
    coefficient = 15
    shelve_clearance_in = 12 / inch_in_mm / coefficient / paper_height 
    panel_thickness = 18 / inch_in_mm / coefficient / paper_height
    mm_37 = 37 / inch_in_mm / coefficient / paper_height
    mm_32 = 32 / inch_in_mm / coefficient / paper_height
    mm_6 = 6 / inch_in_mm / coefficient / paper_height
    mm_5 = 5 / inch_in_mm / coefficient / paper_height
    mm_3 = 3 / inch_in_mm / coefficient / paper_height
    rail = 96 / inch_in_mm / coefficient / paper_height

    def __init__(self, section: list = None):
        self.section = section
        self.wall_section = []
        self.floor_section = []

    def _plot_section(self):
        plt.rcParams["font.size"] = 8
        # Set figure size
        figure = plt.figure(figsize=(self.paper_width, self.paper_height))
        plotting_grid = grid.GridSpec(nrows=1, ncols=1)
        axis_1 = figure.add_subplot(plotting_grid[0, 0])
        # Elevation, box.
        floor_cabinet_widths = [
            cabinet.cabinet_relative_width
            for cabinet in self.floor_section
        ]
        floor_section_total = sum(floor_cabinet_widths)
        horizontal_offset_floor = .5 - (floor_section_total*.5)
        horizontal_offset_wall = .5 - (floor_section_total*.5)
        for index, cabinet in enumerate(self.floor_section):
            vertical_position = .15
            total_height = .15
            if (index != 0):
                horizontal_offset_floor += self.floor_section[index-1].cabinet_relative_width
            axis_1.add_patch(
                Rectangle(
                    xy=(horizontal_offset_floor, vertical_position), 
                    width=cabinet.cabinet_relative_width, 
                    height=cabinet.cabinet_relative_height, 
                    fill=True,
                    facecolor='k'
                )
            )
            if cabinet.drawer_front:
                total_drawer_height = .15
                for index in range(0, len(cabinet.drawer_front)):
                    current_drawer_front_height = \
                        cabinet.drawer_front[index] / self.inch_in_mm / self.coefficient / self.paper_height
                    axis_1.add_patch(
                        Rectangle(
                            xy=(
                                horizontal_offset_floor+(self.mm_3*.5),
                                total_drawer_height
                            ), 
                            width=cabinet.cabinet_relative_width - self.mm_3,  # Compensate for being pushed.
                            height=current_drawer_front_height - (self.mm_3), 
                            fill=True,
                            facecolor='lightgray',
                        )
                    )
                    total_drawer_height += current_drawer_front_height                
            if cabinet.sections:
                sections_bottom_to_top = cabinet.sections_in[::-1]
                for index in range(0, len(sections_bottom_to_top)):
                    current_section_height = \
                        sections_bottom_to_top[index] / self.coefficient / self.paper_height
                    axis_1.add_patch(
                        Rectangle(
                            xy=(
                                horizontal_offset_floor+(self.mm_3*.5),
                                total_height
                            ), 
                            width=cabinet.cabinet_relative_width - self.mm_3,  # Compensate for being pushed.
                            height=current_section_height - (self.mm_3), 
                            fill=True,
                            facecolor='lightgray',
                        )
                    )
                    total_height += current_section_height
        for index, cabinet in enumerate(self.wall_section):
            vertical_position = .65
            total_height = .65
            if (index != 0):
                horizontal_offset_wall += self.wall_section[index-1].cabinet_relative_width
            axis_1.add_patch(
                Rectangle(
                    xy=(horizontal_offset_wall, vertical_position), 
                    width=cabinet.cabinet_relative_width, 
                    height=cabinet.cabinet_relative_height, 
                    fill=True,
                    facecolor='k'
                )
            )
            if cabinet.sections:
                sections_bottom_to_top = cabinet.sections_in[::-1]
                for index in range(0, len(sections_bottom_to_top)):
                    current_section_height = \
                        sections_bottom_to_top[index] / self.coefficient / self.paper_height
                    axis_1.add_patch(
                        Rectangle(
                            xy=(
                                horizontal_offset_wall+(self.mm_3*.5),
                                total_height
                            ), 
                            width=cabinet.cabinet_relative_width - self.mm_3,  # Compensate for being pushed.
                            height=current_section_height - (self.mm_3), 
                            fill=True,
                            facecolor='lightgray',
                        )
                    )
                    total_height += current_section_height
        axis_1.tick_params(labeltop=True, labelright=True)
        axis_1.tick_params(axis='both', direction='in')
        axis_1.tick_params(bottom=True, top=True, left=True, right=True) 
        axis_1.set_xticklabels([])
        axis_1.set_yticklabels([])
        #figure.subplots_adjust(left=.25, right=.75)
        plt.tight_layout()
        plt.savefig(fname='cabinet.pdf', dpi=1200, format='pdf')
        plt.show()

    def _reorder_plots(self):
        for cabinet_plot in self.section:
            match cabinet_plot.cabinet_type:
                case 'wall':
                    self.wall_section.append(cabinet_plot)
                case 'floor':
                    self.floor_section.append(cabinet_plot)
                case 'cupboard':
                    self.floor_section.append(cabinet_plot)

    def plot_section(self):
        self._reorder_plots()
        self._plot_section()

            # Sections.
            # for index, section_pair in enumerate(cabinet.section_pairs_positions):
            #     height = (cabinet.sections_in[index] / self.coefficient / self.paper_height)
            #     y = 1-(section_pair[1][0]+(self.mm_3*.5))
            #     print(y, height)
            #     axis_1.add_patch(
            #         Rectangle(
            #             xy=(
            #                 horizontal_offset+(self.mm_3*.5),
            #                 y
            #             ), 
            #             width=cabinet.cabinet_relative_width - self.mm_3,  # Compensate for being pushed.
            #             height=height - (self.mm_3), 
            #             fill=True,
            #             facecolor='lightgray',
            #         )
            #     )
            # Original sections are listed from top to bottom. In order
            # to draw them it is necessary to reverse the order, because
            # reference point for drawing rectangles in matplotlib is
            # bottom left.
