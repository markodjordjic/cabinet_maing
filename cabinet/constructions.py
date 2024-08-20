import pandas as pd

class BaseCorpus:
    """Dimensions

    """
    def __init__(self,
                 height: int, 
                 width: int, 
                 depth: int, 
                 back_tolerance: int = 2):
        self.height = height
        self.width = width
        self.depth = depth
        self.back_tolerance = back_tolerance
        self.side_edge_banding = None
        self.top_bottom_edge_banding = None


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
                 top_type: str = 'one_piece'):
        super().__init__(height=height, 
                         width=width, 
                         depth=depth, 
                         back_tolerance=back_tolerance)       
        self.top_type = top_type
        self.inner_width = None
        self.material = []
        self.side_edge_banding = "N/A"
        self.top_bottom_edge_banding = "N/A"
        self.top_front_stretcher_banding = "N/A"
        self.top_back_stretcher_banding = "N/A"

    def _compute_inner_width(self):
        
        self.inner_width = self.width - 36
 
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
                'Top front stretcher', 
                self.inner_width, 
                96, 
                1, 
                self.top_front_stretcher_banding
            ],
            [
                'Korpus',
                'Top back stretcher', 
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
    
    def _back(self):

        self.material.append([
            'Lesonit',
            'Back', 
            self.height - 12 - self.back_tolerance, 
            self.width - 12 - self.back_tolerance, 
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
        self._back()
        self._rails()

        return pd.DataFrame.from_records(self.material)


class TopCabinet(Corpus):
    """_summary_

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
                 shelves: int = 0,
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
        back_relief = 4
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
            self.shelves,
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
        shelves = self._shelves()
        doors = self._doors()
        material = pd.concat([corpus_material, shelves, doors])
        material.reset_index(inplace=True, drop=True)

        return material


class BottomCabinet(Corpus):
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
                 drawers: list[int],
                 back_tolerance: int = 2,
                 top_type: str = 'two-piece',
                 top_relief: int = 0,
                 doors: int = 0,
                 front_heights: list[int] = []):
        super().__init__(height=height, 
                         width=width, 
                         depth=depth,
                         top_type=top_type, 
                         back_tolerance=back_tolerance)
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

        back = drawer.get_drawer_back()
      
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
    
    def _compute_stretchers(self):
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

    def compute_total_material(self):
        corpus_material = super().compute_corpus_material()
        drawers = self._compute_drawers()
        material = pd.concat([corpus_material, drawers])
        if len(self.drawers) > 2:
            self._drawer_stretcher_banding()
            drawer_stretcher = self._compute_stretchers()
            material = pd.concat([corpus_material, drawers, drawer_stretcher])
        material.reset_index(inplace=True, drop=True)

        return material


class Drawer(BaseCorpus):

    drawer_front_banding = 'u krug'

    def __init__(self, 
                 height: int, 
                 width: int, depth: int, 
                 back_tolerance: int = 2,
                 top_relief = 0,
                 slide_relief: int = 26,
                 back_relief: int = 50):
        super().__init__(height, width, depth, back_tolerance)
        self.top_relief = top_relief
        self.slide_relief = slide_relief
        self.back_relief = back_relief
        self.drawer_front_height = None
        self.drawer_front_width = None
        self.drawer_box_height = None
        self.drawer_box_width = None
        self.drawer_box_inner_width = None
        self.drawer_box_depth = None
        self.drawer_back = None
        self.drawer_back_height = None
        self.drawer_back_width = None

    def _compute_dimensions(self):
        self.drawer_front_height = self.height - 3
        self.drawer_front_width = self.width - 3
        self.drawer_box_height = self.drawer_front_height + 3 - (24*2)
        self.drawer_box_width = self.width - 36 - (2*self.slide_relief)
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

    def _compute_back(self):
        self.drawer_back_width =  \
            self.drawer_box_inner_width - 12 - self.back_tolerance
        self.drawer_back_height = self.depth - 12 - self.back_tolerance

    def compute_material(self):
        self._compute_dimensions()
        self._compute_banding()
        self._compute_back()

    def get_drawer_box_sides(self):
        
        return [
            'Korpus',
            'Drawer, box (side)',
            self.drawer_box_depth,
            self.drawer_box_height,
            2,
            self.side_edge_banding
        ]

    def get_drawer_front_back(self):
        
        return [
            'Korpus',
            'Drawer, box (face/back)',
            self.drawer_box_inner_width,
            self.drawer_box_height,
            2,
            self.top_bottom_edge_banding
        ]

    def get_drawer_front(self):
        
        return [
            'Front',
            'Drawer, front',
            self.drawer_front_width,
            self.drawer_front_height,
            1,
            self.drawer_front_banding
        ]

    def get_drawer_back(self):
        
        return [
            'Lesonit',
            'Drawer, box (back)',
            self.drawer_back_height,
            self.drawer_back_width,
            1,
            'No banding'
        ]


class Section(BaseCorpus):

    def __init__(self,
                 height: int, 
                 width: int, 
                 depth: int, 
                 back_tolerance: int = 2,
                 room: str = 'Room',
                 section_name: str = 'Section',
                 base_name: str = 'Name',
                 total_units: int = 1,
                 shelves: int = None,
                 dividers: int = 0,
                 stretchers: int = 0,
                 drawers: list[int] = [None],
                 top_relief: int = None,
                 doors: int = None, 
                 cabinet_type: str = 'wall'):
        super().__init__(height=height, 
                         width=width, 
                         depth=depth, 
                         back_tolerance=back_tolerance)       
        self.room = room
        self.section = section_name
        self.base_name = base_name
        self.total_units = total_units
        self.shelves = shelves
        self.dividers = dividers
        self.stretchers = stretchers
        self.drawers = drawers
        self.top_relief = top_relief
        self.doors = doors
        self.cabinet_type = cabinet_type

    def _select_cabinet_type(self):

        if self.cabinet_type == 'wall':
            cabinet = TopCabinet(
                height=self.height,
                width=self.width,
                depth=self.depth,
                back_tolerance=self.back_tolerance,
                shelves=self.shelves,
                doors=self.doors
            )
        
        if self.cabinet_type == 'floor':
            cabinet = BottomCabinet(
                height=self.height,
                width=self.width,
                depth=self.depth,
                back_tolerance=self.back_tolerance,
                drawers=self.drawers,
                top_relief=self.top_relief
            )

        return cabinet

    def make_cabinets(self):
        cabinet_inventory = []
        for index in range(0, self.total_units):
            cabinet_name = self.base_name + ' ' + str(index+1)
            meta = [self.room, self.section, cabinet_name] 
            cabinet = self._select_cabinet_type()
            cabinet_material = cabinet.compute_total_material()
            meta_index = \
                pd.DataFrame.from_records(len(cabinet_material) * [meta])
            cabinet_and_meta = pd.concat(
                (meta_index, cabinet_material), axis=1
            )
            cabinet_and_meta.columns = [
                'Room', 
                'Section', 
                'Name', 
                'Materijal', 
                'Part', 
                'X', 
                'Y', 
                'Units', 
                'Banding'
            ]
            cabinet_inventory.extend([cabinet_and_meta])
        
        return pd.concat(cabinet_inventory)

class Cupboard(Corpus):

    front_edge_banding = 'u krug'

    def __init__(self, 
                 height: int, 
                 width: int, 
                 depth: int, 
                 back_tolerance: int, 
                 top_type: str = 'one_piece',
                 h_dividers: int = 0,
                 shelves: int = 0,
                 drawers: int = 0,
                 drawer_face_height: int = 0,
                 front_sections: list[int] = [0],
                 doors_per_section: list[int] = [1]):
        super().__init__(height=height, 
                         width=width, 
                         depth=depth, 
                         back_tolerance=back_tolerance, 
                         top_type=top_type)
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
        back_relief = 4
        self.h_divider_depth = self.depth - back_relief

    def _compute_shelf_depth(self):
        back_relief = 4
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
        self.material.extend([[
            'Korpus',
            'Horizontal Dividers',
            self.inner_width,
            self.h_divider_depth,
            self.h_dividers,
            self.h_dividers_banding
        ]])
        self.material.extend([[
            'Korpus',
            'Rails',
            self.inner_width,
            96,
            self.h_dividers,
            'jedna duza'
        ]])

    def _compute_shelves(self):
        self.material.extend([[
            'Korpus',
            'Shelves',
            self.inner_width,
            self.shelf_depth,
            self.shelves,
            self.shelf_banding
        ]])

    def _compute_drawers(self):

        if self.drawers > 0:

            assert self.drawer_face_height % 32 == 0, \
                'Drawer dimension not correct.'

            top_relief = 0
            slide_relief = 25
            back_relief = 50

            drawer = Drawer(
                height=self.drawer_face_height,
                width=self.width,
                depth=self.depth,
                back_tolerance=2,
                top_relief=top_relief,
                slide_relief=slide_relief,
                back_relief=back_relief,
                drawers=self.drawers
            )

            drawer.compute_material()
            
            self.material.extend([drawer.get_drawer_box_sides()])
            
            self.material.extend([drawer.get_drawer_front_back()])

            self.material.extend([drawer.get_drawer_back()])

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

