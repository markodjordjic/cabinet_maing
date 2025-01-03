import pandas as pd
from cabinet_making.base_classes import BaseCorpus

class Corpus(BaseCorpus):
    """Dimensions and edge banding according to Corpus type

    Parameters
    ----------
    BaseCorpus : (str) Indication of corpus type
        `Top` or `Bottom` cabinets

    """

    def __init__(self,
                 height: int,
                 width: int,
                 depth: int,
                 back_tolerance: int,
                 top_type: str = 'one-piece', 
                 back: bool = True):
        super().__init__(height=height, 
                         width=width, 
                         depth=depth, 
                         back_tolerance=back_tolerance)       
        self.top_type = top_type
        self.back = back
        self.inner_width = None
        self.material = []
        self.side_edge_banding = "N/A"
        self.top_bottom_edge_banding = "N/A"
        self.top_front_stretcher_banding = "N/A"
        self.top_back_stretcher_banding = "N/A"

    def _compute_inner_width(self):

        material_thickness = 18
        
        self.inner_width = self.width - (material_thickness*2)
 
    def _sides(self):

        self.material.append([
            'Korpus',
            'Sides', 
            self.height, 
            self.depth, 
            2,
            self.side_edge_banding
        ])
    
    def _one_piece_top(self):

        self.material.append([
            'Korpus',
            'Top/bottom', 
            self.inner_width, 
            self.depth,
            2,
            self.top_bottom_edge_banding
        ])
    
    def _two_piece_top(self):
        
        self.material.extend([  
            [   
                'Korpus',
                'Bottom', 
                self.inner_width,
                self.depth, 
                1, 
                self.top_bottom_edge_banding
            ],
            [
                'Korpus',
                'Top front/back stretcher', 
                self.inner_width, 
                96, 
                1, 
                self.top_front_stretcher_banding
            ],
            [
                'Korpus',
                'Top front/back stretcher', 
                self.inner_width, 
                96, 
                1, 
                self.top_back_stretcher_banding
            ]
        ])
    
    def _top_and_bottom(self):

        if self.top_type == 'one-piece':
            self._one_piece_top()

        if self.top_type == 'two-piece':
            self._two_piece_top()

    def _back_groove(self):
        """Generate material list for the back with groove

        """

        material_remainder = 10

        self.material.append([
            'Lesonit',
            'Back', 
            self.height - (2*material_remainder) - self.back_tolerance, 
            self.width - (2*material_remainder) - self.back_tolerance, 
            1,
            'No edge banding'
        ])


    def _back(self):
        """Generate material list for the back with rabbet

        """
        material_remainder = 6

        self.material.append([
            'Lesonit',
            'Back', 
            self.height - (2*material_remainder) - self.back_tolerance, 
            self.width - (2*material_remainder) - self.back_tolerance, 
            1,
            'No edge banding'
        ])

    def _validate_dimensions(self):

        assert self.height % 32 == 0, 'Height not a multiple of 32.'
        assert self.width % 32 == 0, 'Width not a multiple of 32.'
        assert self.depth % 32 == 0, 'Depth not a multiple of 32.'

    def _rails(self):

        self.material.append(
            ['Korpus', 'Rails', self.inner_width, 96, 2, 'jedna duza']
        )

    def _banding(self):

        if self.inner_width > self.depth:
            self.top_bottom_edge_banding = 'dve duze'
        
        if self.inner_width < self.depth:
            self.top_bottom_edge_banding = 'dve krace'

        self.side_edge_banding = 'u krug'

        if self.inner_width > 96:
            self.top_back_stretcher_banding = 'dve duze'
            self.top_front_stretcher_banding = 'dve duze'

        if self.inner_width < 96:
            self.top_back_stretcher_banding = 'dve krace'
            self.top_front_stretcher_banding = 'dve krace'

    def compute_corpus_material(self):
        self._validate_dimensions()
        self._compute_inner_width()
        self._banding()
        self._sides()
        self._top_and_bottom()
        if self.back:
            self._back()
        self._rails()

        return pd.DataFrame.from_records(self.material)


class WallCabinet(Corpus):
    """Wall cabinet measurements and edge banding

    Parameters
    ----------
    Corpus : _type_
        _description_

    Returns
    -------
    _type_
        _description_

    """

    door_edge_banding = 'u krug'

    def __init__(self, 
                 height: int, 
                 width: int, 
                 depth: int, 
                 top_type: str = 'one-piece',
                 back_tolerance: int = 2, 
                 shelves: int = None,  # TODO: List of heights, or count?
                 doors: int = 1):
        super().__init__(height=height, 
                         width=width, 
                         depth=depth,
                         top_type=top_type,
                         back_tolerance=back_tolerance)
        self.shelves = shelves
        self.doors = doors
        self.shelf_depth = None
        self.shelf_edge_banding = None

    def _compute_shelf_depth(self):
        front_relief = 6
        back_relief = 6
        self.shelf_depth = self.depth - front_relief - back_relief

    def _shelf_edge_banding(self):

        if self.inner_width > self.shelf_depth:
            edge_banding = 'jedna duza'
        else:
            edge_banding = 'jedna kraca'

        self.shelf_edge_banding = edge_banding

    def _shelves(self):
        self._compute_shelf_depth()
        self._shelf_edge_banding()

        return pd.DataFrame.from_records([[
            'Korpus',
            'Shelves', 
            self.inner_width, 
            self.shelf_depth, 
            len(self.shelves),  # Shelve count.
            self.shelf_edge_banding
        ]])
    
    def _doors(self):
        vertical_relief = 0
        horizontal_relief = 3
        door_width = (self.width/self.doors) - horizontal_relief
        door_height = self.height - vertical_relief
        
        return pd.DataFrame.from_records([[
            'Front',
            'Door', 
            door_height, 
            door_width, 
            self.doors, 
            self.door_edge_banding
        ]])
    
    def _sides_edge_banding(self):
        if self.height > self.depth:
            self.side_edge_banding = 'jedna duza, dve krace'
        if self.height < self.depth:
            self.side_edge_banding = 'jedna kraca, dve duze'

    def compute_total_material(self):
        self._sides_edge_banding()
        corpus_material = super().compute_corpus_material()
        shelves = pd.DataFrame()  # Place-holder.
        if self.shelves:
            shelves = self._shelves()
        doors = self._doors()
        material = pd.concat([corpus_material, shelves, doors])
        material.reset_index(inplace=True, drop=True)

        return material


class FloorCabinet(Corpus):
    """Generic bottom cabinets

    Parameters
    ----------
    Corpus : _type_
        _description_

    Returns
    -------
    _type_
        _description_

    """

    drawer_front_banding = 'u krug'

    def __init__(self, 
                 height: int, 
                 width: int, 
                 depth: int, 
                 drawers: list[int],  # Height of each drawer w/o gap/reveal.
                 back_tolerance: int = 2,
                 top_type: str = 'two-piece',
                 top_relief: int = 0,
                 doors: int = None,
                 sections: list[int] = None,
                 doors_per_section: list[int] = None,
                 front_heights: list[int] = None):
        super().__init__(height=height, 
                         width=width, 
                         depth=depth,
                         top_type=top_type, 
                         back_tolerance=back_tolerance)
        self.sections = sections
        self.doors = doors
        self.doors_per_section = doors_per_section
        self.drawers = drawers
        self.top_relief = top_relief
        self.drawer_stretcher_banding = 'N/A'

    def _drawer_stretcher_banding(self):
        if self.inner_width > 96:
            self.drawer_stretcher_banding = 'dve duza'
        else:
            self.drawer_stretcher_banding = 'dve krace'
    
    def _compute_drawer(self, front_height):
        slide_relief = 26  # Attention!
        back_relief = 50

        drawer = Drawer(
            height=front_height,
            width=self.width,
            depth=self.depth,
            back_tolerance=2,
            top_relief=self.top_relief,
            slide_relief=slide_relief,
            back_relief=back_relief
        )

        drawer.compute_material()
        box_sides = drawer.get_drawer_box_sides()
        box_front_back = drawer.get_drawer_front_back()
        back = drawer.get_drawer_bottom()     
        front = drawer.get_drawer_front()

        return pd.DataFrame.from_records([
            box_sides, box_front_back, front, back
        ])
    
    def _compute_drawers(self):
        drawers = []
        for drawer in self.drawers:
            drawer = self._compute_drawer(front_height=drawer)
            drawers.extend([drawer])

        return pd.concat(drawers)
    
    def _compute_doors(self) -> pd.DataFrame:
        """_summary_

        Returns
        -------
        pd.DataFrame
            _description_

        """
        doors = []
        for index, section_height in enumerate(self.sections):
            doors_per_section = self.doors_per_section[index]
            if doors_per_section == 0:
                pass
            if doors_per_section >= 1:
                width = (self.width/doors_per_section) - 3
                doors.append([
                    'Front',
                    f'Section {section_height}, door',
                    width,
                    section_height - 3,
                    doors_per_section,
                    'u krug'
                ])

        return pd.DataFrame.from_records(doors)

    def _compute_stretchers(self) -> list:
        
        return pd.DataFrame.from_records(
                [[
                    'Korpus',
                    'Drawer stretcher',
                    self.inner_width,
                    96,
                    len(self.drawers) - 1,
                    self.drawer_stretcher_banding
                ]]
            )
    def _validate_section_dimensions(self):
        """Vaildates dimensions of individual sections

        Sum of all sections must be equal to cabinet height. See notes.

        Notes
        -----
        This does not mean that all sections must have doors.
        
        """
        if self.sections:
            assert sum(self.sections) == self.height           

    def compute_total_material(self):
        self._validate_section_dimensions()        
        corpus_material = super().compute_corpus_material()
        output = corpus_material  # Mandatory.
        drawers = pd.DataFrame()  # Place-holder.
        drawer_stretcher = pd.DataFrame()  # Placeholder.
        doors = pd.DataFrame()  # Place-holder.
        if self.drawers:
            drawers = self._compute_drawers()
            output = pd.concat([corpus_material, drawers])
            if len(self.drawers) > 2:
                self._drawer_stretcher_banding()
                drawer_stretcher = self._compute_stretchers()
                output = pd.concat([
                    corpus_material, 
                    drawers, 
                    drawer_stretcher
                ])
        if self.doors:
            doors = self._compute_doors()
            output = pd.concat([
                corpus_material, 
                drawers, 
                drawer_stretcher, 
                doors
            ])
        output.reset_index(inplace=True, drop=True)

        return output


class Drawer(BaseCorpus):

    drawer_front_banding = 'u krug'

    def __init__(self,
                 height: int, 
                 width: int, 
                 depth: int, 
                 count: int = 1, 
                 back_tolerance: int = 2,
                 top_relief = 0,
                 slide_relief: int = 26,
                 back_relief: int = 50):
        super().__init__(height, width, depth, back_tolerance)
        self.top_relief = top_relief
        self.slide_relief = slide_relief
        self.back_relief = back_relief
        self.count = count
        self.drawer_front_height = None
        self.drawer_front_width = None
        self.drawer_box_height = None
        self.drawer_box_width = None
        self.drawer_box_inner_width = None
        self.drawer_box_depth = None
        self.drawer_back = None
        self.drawer_bottom_width = None
        self.drawer_bottom_depth = None

    def _compute_dimensions(self):
        self.drawer_front_height = self.height - 3
        self.drawer_front_width = self.width - 3
        self.drawer_box_height = self.drawer_front_height + 3 - (24*2)
        self.drawer_box_width = self.width - 36 - self.slide_relief
        self.drawer_box_inner_width = self.drawer_box_width - 36
        self.drawer_box_depth = self.depth - self.back_relief

    def _compute_banding(self):
        if self.drawer_box_inner_width > self.drawer_box_height:
            self.side_edge_banding = 'dve duze, jedna kraca'
        if self.drawer_box_inner_width < self.drawer_box_height:
            self.side_edge_banding = 'dve krace, jedna duza'
        if self.drawer_box_depth > self.drawer_box_height:
            self.top_bottom_edge_banding = 'dve duze'
        if self.drawer_box_depth < self.drawer_box_height:
            self.top_bottom_edge_banding = 'dve krace'

    def _compute_bottom(self):
        self.drawer_bottom_width =  \
            self.drawer_box_width - (2*12) - self.back_tolerance
        self.drawer_bottom_depth = \
            self.drawer_box_depth - (2*12) - self.back_tolerance

    def get_drawer_box_sides(self):
        
        return [
            'Korpus',
            'Drawer, box (side)',
            self.drawer_box_depth,
            self.drawer_box_height,
            2*self.count,
            self.side_edge_banding
        ]

    def get_drawer_front_back(self):
        
        return [
            'Korpus',
            'Drawer, box (face/back)',
            self.drawer_box_inner_width,
            self.drawer_box_height,
            2*self.count,
            self.top_bottom_edge_banding
        ]

    def get_drawer_front(self):
        
        return [
            'Front',
            'Drawer, front',
            self.drawer_front_width,
            self.drawer_front_height,
            1*self.count,
            self.drawer_front_banding
        ]

    def get_drawer_bottom(self):
        
        return [
            'Lesonit',
            'Drawer, box (bottom)',
            self.drawer_bottom_width,
            self.drawer_bottom_depth,
            1*self.count,
            'No banding'
        ]
    
    def compute_material(self):
        self._compute_dimensions()
        self._compute_banding()
        self._compute_bottom()

class Cupboard(Corpus):

    front_edge_banding = 'u krug'
    top_type = 'one-piece'

    def __init__(self, 
                 height: int, 
                 width: int, 
                 depth: int, 
                 back_tolerance: int, 
                 h_dividers: int = 0,
                 shelves: int = 0,
                 drawers: int = 0,
                 drawer_face_height: list = [],
                 front_sections: list[int] = [0],
                 doors_per_section: list[int] = [1]):
        super().__init__(height=height, 
                         width=width, 
                         depth=depth, 
                         back_tolerance=back_tolerance, 
                         top_type=self.top_type)
        self.h_dividers = h_dividers
        self.h_divider_depth = None
        self.h_dividers_banding = 'N/A'
        self.shelves = shelves
        self.shelf_depth = None
        self.shelf_banding = 'N/A'
        self.drawers = drawers
        self.drawer_face_height = drawer_face_height
        self.front_sections = front_sections
        self.doors_per_section = doors_per_section

    def _compute_h_divider_depth(self):
        back_relief = 6
        self.h_divider_depth = self.depth - back_relief

    def _compute_shelf_depth(self):
        back_relief = 6
        front_relief = 6
        self.shelf_depth = self.depth - back_relief - front_relief

    def _compute_banding(self):
        # h-dividers
        if self.inner_width > self.h_divider_depth:
            self.h_dividers_banding = 'jedna duza'

        if self.inner_width < self.h_divider_depth:
            self.h_dividers_banding = 'jedna kraca'

        # shelves
        if self.inner_width > self.shelf_depth:
            self.shelf_banding = 'jedna duza'

        if self.inner_width < self.shelf_depth:
            self.shelf_banding = 'jedna kraca'

    def _compute_front_sections(self):
        pass

    def _compute_h_dividers(self):
        if self.h_dividers:
            self.material.extend([[
                'Korpus',
                'Horizontal Dividers',
                self.inner_width,
                self.h_divider_depth,
                len(self.h_dividers),
                self.h_dividers_banding
            ]])
            self.material.extend([[
                'Korpus',
                'Rails',
                self.inner_width,
                96,
                len(self.h_dividers),
                'jedna duza'
            ]])

    def _compute_shelves(self):
        if self.shelves > 0:
            self.material.extend([[
                'Korpus',
                'Shelves',
                self.inner_width,
                self.shelf_depth,
                self.shelves-self.h_dividers-1,
                self.shelf_banding
            ]])

    def _compute_drawers(self):

        if self.drawers:

            for drawer_face_height in self.drawer_face_height: 

                assert drawer_face_height % 32 == 0, \
                    'Drawer dimension not correct.'

                top_relief = 0
                slide_relief = 25
                back_relief = 50

                drawer = Drawer(
                    height=drawer_face_height,
                    width=self.width,
                    depth=self.depth,
                    count=1,
                    back_tolerance=2,
                    top_relief=top_relief,
                    slide_relief=slide_relief,
                    back_relief=back_relief
                )

                drawer.compute_material()
                
                self.material.extend([drawer.get_drawer_box_sides()])
                
                self.material.extend([drawer.get_drawer_front_back()])

                self.material.extend([drawer.get_drawer_bottom()])

    def _compute_doors(self):
        sections_total = sum(self.front_sections)

        assert sections_total == self.height, 'Sections not correct.'

        assert len(self.front_sections) == len(self.doors_per_section), \
            'Unequal number of doors'

        individual_section_heights = [
            section_height-3 for section_height in self.front_sections
        ]

        individual_section_widths = [
            (self.width/doors_per_section) - 3
            for doors_per_section in self.doors_per_section
        ]

        for heights, widths, count in zip(individual_section_heights,
                                          individual_section_widths,
                                          self.doors_per_section):
            self.material.extend([[
                'Front',
                'Door',
                heights,
                widths,
                count,
                self.front_edge_banding
            ]])                   
      
    def compute_total_material(self):
        super().compute_corpus_material()
        self._compute_h_divider_depth()
        self._compute_shelf_depth()
        self._compute_banding()
        self._compute_h_dividers()
        self._compute_shelves()
        self._compute_front_sections()
        self._compute_drawers()
        self._compute_doors()

        return pd.DataFrame.from_records(self.material)

class SectionBase:
    """Base for the whole section

    Returns
    -------
    _type_
        _description_
    """

    height = 96
    front_back_banding = 'bez kantovanja'
    rib_banding = 'bez kantovanja'

    def __init__(self,
                 depth: int,
                 unit_width: int,
                 unit_count: int,
                 compensation: int = 0) -> None:
        self.depth = depth
        self.unit_width = unit_width
        self.unit_count = unit_count
        self.width = (unit_width*unit_count) + compensation
        self._base_depth = None
        self._inner_width = None
        self.material = []

    def _compute_base_depth(self):
        self._base_depth = self.depth - 64

    def _compute_inner_width(self):
        self._inner_width = self._base_depth - (2*18)

    def _font_back(self):

        self.material.append([
            'Korpus',
            'Base, front/back', 
            self.height, 
            self.width, 
            2,
            self.front_back_banding
        ])

    def _ribs(self):

        self.material.append([
            'Korpus',
            'Base, ribs', 
            self.height,
            self._inner_width, 
            self.unit_count+1,
            self.rib_banding
        ])
    
    def _rails(self):

        self.material.append([
            'Korpus',
            'Base, rails',
            self.height,
            self._inner_width, 
            self.unit_count+1,
            'jedna_duza'
        ])

    def compute_base_material(self):
        self._compute_base_depth()
        self._compute_inner_width()
        self._font_back()
        self._ribs()
        self._rails()

        return pd.DataFrame.from_records(self.material)


    