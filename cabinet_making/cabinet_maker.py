from pathlib import Path
from cabinet_making.constructions import FloorCabinet, WallCabinet, Cupboard
from cabinet_making.measurements import CupboardElevation
from cabinet_making.plots import CabinetPlotter


class CabinetMaker:
    """Cabinet elevation and plotting

    Wrapper around `CupboardEevation` and `CabinetPlotter` classes
    in order to reduce duplication, make code more compact, and easier
    to use.

    """

    def __init__(self,
                 cabinet_type: str = 'floor',
                 cabinet_name: str = None,
                 orientation: str = 'portrait',
                 height: int = None, 
                 depth: int = None, 
                 width: int = None,
                 dividers: list[int] = None,
                 shelves: list[int] = None,
                 drawers: list[int] = None,
                 drawer_reference: int = 0,
                 drawer_front: list[int] = None,
                 sections: list[int] = None,
                 doors_per_section: list[int] = None) -> None:
        self.cabinet_type = cabinet_type
        self.cabinet_name = cabinet_name
        self.orientation = orientation
        self.height_mm = height
        self.depth_mm = depth
        self.width_mm = width
        self.dividers = dividers
        self.drawers = drawers
        self.drawer_front = drawer_front
        self.drawer_reference = drawer_reference
        self.shelves = shelves
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
        self.section_pairs = None
        self.section_positions = None
        self.system_holes = None
        self.section_pairs_positions = None
        self.measurements = None
        self.cabinet = None
        self.plotter = None

    def _make_elevation(self):
        elevation_file = Path(self.cabinet_name + '_elevation.xlsx')
        self.cabinet = CupboardElevation(
            height=self.height_mm,
            sections=self.sections,
            elevation_file=elevation_file,
            drawers=self.drawer_front,
            dividers=self.dividers,
            shelves=self.shelves,
            drawer_reference=self.drawer_reference
        )
        self.cabinet.compute_elevation()
        self.cabinet.write_elevation()

    def _plotting(self):
        plot_file = Path(self.cabinet_name + '_section_and_elevation.pdf')
        self.plotter = CabinetPlotter(
            cabinet_type=self.cabinet_type,
            orientation=self.orientation,
            height=self.height_mm,
            depth=self.depth_mm,
            width=self.width_mm,
            dividers=self.dividers,
            shelves=self.shelves,
            drawers=self.cabinet.get_drawers(),
            drawer_front=self.drawer_front,
            sections=self.sections,
            doors_per_section=self.doors_per_section,
            section_pairs=self.cabinet.get_section_indications(),
            system_holes=self.cabinet.get_system_holes(),
        )
        self.plotter.plot_cabinet(compute_only=True, plot_file=plot_file)

    def _compute_material(self):
        match self.cabinet_type:
            case 'floor':
                measurements = FloorCabinet(
                    height=self.height_mm,
                    width=self.width_mm,
                    depth=self.depth_mm,
                    drawers=self.drawers,
                    doors=0,
                    sections=self.sections,
                    doors_per_section=self.doors_per_section          
                )
            case 'wall':
                measurements = WallCabinet(
                    height=self.height_mm,
                    width=self.width_mm,
                    depth=self.depth_mm,
                    doors=1,  # Doors need to be added to the CabinetMaker class.        
                )
            case 'cupboard':
                measurements = Cupboard(
                    back_tolerance=6,
                    height=self.height_mm,
                    width=self.width_mm,
                    depth=self.depth_mm,
                    front_sections=self.sections,
                    drawers=self.drawer_front,
                    h_dividers=self.dividers,
                    doors_per_section=[1, 1]
                )

        material = measurements.compute_total_material()
        self.measurements = material
 
    def make_cabinet(self):
        self._compute_material()
        self._make_elevation()
        self._plotting()
