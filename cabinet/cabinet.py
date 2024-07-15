import pandas as pd

class BaseCorpus:
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

    def __init__(self,
                 height: int,
                 width: int,
                 depth: int,
                 back_tolerance: int,
                 top_type: str = 'one_piece'):
        super().__init__(height, width, depth, back_tolerance)       
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

        if self.top_type == 'one_piece':
            self._one_piece_top()

        if self.top_type == 'two_piece':
            self._two_piece_top()
    
    def _back(self):

        self.material.append([
            'Lesonit',
            'Back', 
            self.height-12-self.back_tolerance, 
            self.width-12-self.back_tolerance, 
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

        if self.inner_width < 96:
            self.top_back_stretcher_banding = 'dve krace'

    def compute_corpus_material(self):
        self._validate_dimensions()
        self._compute_inner_width()
        self._banding()
        self._sides()
        self._top_and_bottom()
        self._back()
        self._rails()

        #return pd.DataFrame.from_records(self.material)

        # if self.top_type == 'two-piece':
        #     output = pd.DataFrame.from_records([sides, *tops_and_bottoms, back])

        return pd.DataFrame.from_records(self.material)


class TopCabinet(Corpus):

    def __init__(self, 
                 height: int, 
                 width: int, 
                 depth: int, 
                 back_tolerance: int = 2, 
                 top_type: str = 'one_piece',
                 shelves: int = 0,
                 doors: int = 1):
        super().__init__(height, width, depth, back_tolerance, top_type)
        self.shelves = shelves
        self.doors = doors
        self.shelf_depth = None
        self.shelf_edge_banding = None
        self.door_edge_banding = 'u krug'

    def _compute_shelf_depth(self):
        front_relief = 4
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

        return pd.DataFrame.from_records(
            [[
                'Korpus',
                'Shelves', 
                self.inner_width, 
                self.shelf_depth, 
                self.shelves,
                self.shelf_edge_banding
            ]]
        )
    
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

    def compute_corpus_material(self):
        self._sides_edge_banding()
        corpus_material = super().compute_corpus_material()
        shelves = self._shelves()
        doors = self._doors()
        material = pd.concat([corpus_material, shelves, doors])
        material.reset_index(inplace=True, drop=True)

        return material


class BottomCabinet(Corpus):

    top_type = 'two_piece'
    drawer_front_banding = 'u krug'

    def __init__(self, 
                 height: int, 
                 width: int, 
                 depth: int, 
                 back_tolerance: int = 2, 
                 drawers: int = 0):
        super().__init__(height, width, depth, back_tolerance)
        self.drawers = drawers

    def _compute_drawers(self):
        top_relief = 0
        slide_relief = 25
        back_relief = 50

        drawer = Drawer(
            height=self.height,
            width=self.width,
            depth=self.depth,
            back_tolerance=2,
            top_relief=top_relief,
            slide_relief=slide_relief,
            back_relief=back_relief,
            drawers=self.drawers
        )

        drawer.compute_material()
        
        box_sides = drawer.get_drawer_box_sides()
        
        box_front_back = drawer.get_drawer_front_back()

        back = drawer.get_drawer_back()
      
        front = drawer.get_drawer_front()

        return pd.DataFrame.from_records([
            box_sides, box_front_back, front, back
        ])

    def compute_corpus_material(self):
        corpus_material = super().compute_corpus_material()
        drawers = self._compute_drawers()
        material = pd.concat([corpus_material, drawers])
        material.reset_index(inplace=True, drop=True)

        return material


class Drawer(BaseCorpus):

    drawer_front_banding = 'u krug'

    def __init__(self, 
                 height: int, 
                 width: int, 
                 depth: int, 
                 back_tolerance: int = None,  # Bottom tolerance
                 top_relief = 0,
                 drawers: int = 1,
                 slide_relief: int = 25,
                 back_relief: int = 50):
        super().__init__(height, width, depth, back_tolerance)
        self.drawers = drawers
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
        self.drawer_front_height = \
            self.height - self.top_relief - 3*self.drawers
        self.drawer_front_width = self.width - 3
        self.drawer_box_height = self.drawer_front_height - 25*2
        self.drawer_box_width = self.width - 36 - self.slide_relief
        self.drawer_box_inner_width = self.drawer_box_width - 36
        self.drawer_box_depth = self.depth - self.back_relief

    def _compute_banding(self):
        if self.drawer_box_inner_width > self.drawer_box_height:
            self.side_edge_banding = 'dve duze'
        if self.drawer_box_inner_width < self.drawer_box_height:
            self.side_edge_banding = 'dve krace'
        if self.drawer_box_depth > self.drawer_box_height:
            self.top_bottom_edge_banding = 'dve duze, jedna kraca'
        if self.drawer_box_depth < self.drawer_box_height:
            self.top_bottom_edge_banding = 'dve krace, jedna duza'

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
            'Drawer, box, side',
            self.drawer_box_depth,
            self.drawer_box_height,
            self.drawers*2,
            self.side_edge_banding
        ]

    def get_drawer_front_back(self):
        return [
            'Korpus',
            'Drawer, box, front/back',
            self.drawer_box_height,
            self.drawer_box_inner_width,
            self.drawers*2,
            self.top_bottom_edge_banding
        ]

    def get_drawer_front(self):
        return [
            'Front',
            'Drawer, box, front',
            self.drawer_front_height,
            self.drawer_front_width,
            self.drawers,
            self.drawer_front_banding
        ]

    def get_drawer_back(self):
        return [
            'Lesonit',
            'Drawer, back',
            self.drawer_back_height,
            self.drawer_back_width,
            self.drawers,
            'No banding'
        ]


class Section:

    def __init__(self,
                 height: int, 
                 width: int, 
                 depth: int, 
                 shelves: int,
                 room: str = 'Room',
                 section: str = 'Section',
                 base_name: str = 'Name',
                 total_units: int = 1, 
                 back_tolerance: int = 2,
                 dividers: int = 0,
                 stretchers: int = 0,
                 top: str='one_piece',
                 drawers: int = 0):
        self.room = room
        self.section = section
        self.base_name = base_name
        self.total_units = total_units
        self.height = height
        self.width = width
        self.depth = depth
        self.shelves = shelves
        self.back_tolerance = back_tolerance
        self.dividers = dividers
        self.stretchers = stretchers
        self.top = top
        self.drawers = drawers

    def make_cabinets(self):
        cabinet_inventory = []
        for index in range(0, self.total_units):
            cabinet_name = self.base_name + ' ' + str(index+1)
            meta = [self.room, self.section, cabinet_name] 
            cabinet = BottomCabinet(
                height=self.height,
                width=self.width,
                depth=self.depth,
                # shelves=self.shelves,
                # top_type=self.top,
                back_tolerance=self.back_tolerance,
                drawers=self.drawers
            )
            cabinet_material = cabinet.compute_corpus_material()
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

if __name__ == '__main__':

    section = Section(
        room='Kitchen',
        section='Top',
        base_name='Right',
        total_units=5,
        height=800,
        width=448,
        depth=608,
        shelves=2,
        top='one_piece',
        back_tolerance=2
    )

    kitchen_top = section.make_cabinets()

    summary = kitchen_top.groupby(by=['Part', 'X', 'Y']).aggregate({
        'Units': sum,
        'Banding': min
    })