from math import ceil
import pandas as pd
import numpy as np
from cabinet_making.base_classes import BaseElevation

class CupboardElevation(BaseElevation):

    def __init__(self,
                 height: int,
                 sections: list[int] = [],
                 drawers: list[int] = [],
                 dividers: list[int] = [],
                 shelves: int = None,
                 elevation_file: str = None) -> None:
        super().__init__(height, sections, drawers, dividers, shelves)
        self.elevation_file = elevation_file
        self._positions = None
        self._section_indications = None

    def _create_positions(self):
        positions = []
        for position in range(0, self.height, 32):
            positions.extend([position])

        # Compensation for omission of last item in `range`.
        positions.append(self.height)

        positions_table = pd.DataFrame.from_records(
            [positions, positions[::-1]]
        )
        self._positions = positions_table.transpose()
        self._positions['skip_indication'] = 'USABLE'
        self._positions['hinge_indication'] = '-'
        self._positions['drawer_indication'] = '-'
        self._positions['shelf_indication'] = '-'
        self._positions['divider_indication'] = '-'

    def _indicate_sections(self):
        # Section starts, and section ends.
        zero_padding = [0] + self.sections        
        cumulative_heights = np.cumsum(zero_padding)
        pairs = [
            [cumulative_heights[i], cumulative_heights[i + 1]]
            for i in range(len(cumulative_heights) - 1)
        ]
        self._section_indications = pairs

    def _indicate_hinges(self):
        hinge_positions = []
        hinge_positions_label = []
        for index, pair in enumerate(self._section_indications):
            top_hinge_start = pair[0] + 64  # Top hinge hole.
            top_hinge_end = pair[0] + 96  # Bottom hinge hole.
            bottom_hinge_start = pair[1] - 96
            bottom_hinge_end = pair[1] - 64
            hinge_positions.extend([
                top_hinge_start, 
                top_hinge_end, 
                bottom_hinge_start, 
                bottom_hinge_end
            ])
            hinge_positions_label.extend([
                f"Section {index}, top hinge (first hole)",
                f"Section {index}, top hinge (second hole)",
                f"Section {index}, bottom hinge (first hole)",
                f"Section {index}, bottom hinge (second hole)"
            ])
        # Make markings for system holes.
        for index, hinge_position in enumerate(hinge_positions):
            selection = self._positions.iloc[:, 0] == hinge_position
            self._positions.loc[selection, 'hinge_indication'] = \
                hinge_positions_label[index]
            
    def _indicate_drawers(self):
        #top_bottom_clarence = 48
        drawer_face_height = [160, 160, 160, 160]  # With gaps/reveals.
        starting_position = [96]
        drawers_from_bottom = starting_position + drawer_face_height        
        cumulative_drawer_heights = np.cumsum(drawers_from_bottom)
        drawer_indices = []
        drawer_indices_labels = []
        for index, drawer_face in enumerate(drawer_face_height):
            # One less iteration then cumulative heights, because of different
            # lengths.
            drawer_vertical_center = drawer_face / 2
            drawer_index = cumulative_drawer_heights[index] + drawer_vertical_center
            drawer_indices.extend([drawer_index])
            drawer_indices_labels.extend([f"Drawer slide {index}"])
        for index, drawer_index in enumerate(drawer_indices):
            selection = self._positions.iloc[:, 1] == drawer_index - 16  # TODO: Addition or subtraction!
            self._positions.loc[selection, 'drawer_indication'] = drawer_indices_labels[index]

    def _indicate_shelves(self):
        shelve_positions_label = []
        #shelf_heights =  [self.shelves]*int(self.height/self.shelves)
        shelf_heights = self.shelves
        # starting_position = [0]
        # drawers_from_bottom = starting_position + shelf_heights        
        # shelve_positions = np.cumsum(drawers_from_bottom)
        shelve_positions = self.shelves
        for index, _ in enumerate(shelf_heights):
            # One less iteration then cumulative heights, because of different
            # lengths.
            shelve_positions_label.extend([f"Shelve {index}"])
        for index, _ in enumerate(shelf_heights):  # From bottom.
            selection = self._positions.iloc[:, 1] == shelve_positions[index]
            self._positions.loc[selection, 'shelf_indication'] = \
                shelve_positions_label[index] 
            
    def _indicate_dividers(self):
        divider_label = []
        for index, _ in enumerate(self.dividers):
            # One less iteration then cumulative heights, because of different
            # lengths.
            divider_label.extend([f"Divider {index}"])
        for index, divider in enumerate(self.dividers):  # From top
            selection = self._positions.iloc[:, 0] == divider
            self._positions.loc[selection, 'divider_indication'] = \
                divider_label[index]

    def _make_indications(self): 
        # Make markings for rail indications.
        start_indices = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1         
        ]
        rail_indices = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1
        ]
        terminate = False
        last_take_end_index = 0
        take = 1
        while terminate is not True:
            column_name = f'rail_indices_take_{take}'
            if take == 1:
                indices = start_indices
            else:
                indices = rail_indices
            repeats_before = np.repeat(
                np.nan, 
                repeats=last_take_end_index
            ).tolist()
            repeats = len(self._positions) - len(indices) - len(repeats_before)
            if repeats >= 0:
                repeats_after = np.repeat(
                    np.nan, 
                    repeats=(len(self._positions)-len(indices)-len(repeats_before))
                ).tolist()
            else:
                truncated_indices = indices[0:len(indices)+repeats]
                indices = truncated_indices
                repeats_after = []
            self._positions[column_name] = \
                repeats_before + indices + repeats_after
            where_are_we = self._positions.apply(
                lambda series: series.last_valid_index()
            )[column_name]
            terminate = \
                True if (where_are_we+1) == len(self._positions) else False
            hinge_indication = self._positions['hinge_indication'] == '-'
            slide_indication = self._positions['drawer_indication'] == '-'
            shelve_indication = self._positions['shelf_indication'] == '-'
            divider_indication = \
                self._positions['divider_indication'] == '-'
            markings = np.all([
                hinge_indication, 
                slide_indication, 
                shelve_indication, 
                divider_indication
            ], axis=0)
            self._positions.loc[markings, column_name] = np.nan
            last_take_end_index_in_loop = self._positions.apply(
                lambda series: series.last_valid_index()
            )[column_name]
            # Needed to avoid permanent loop.
            if (last_take_end_index >= last_take_end_index_in_loop) or np.isnan(last_take_end_index_in_loop):
                extension_hole = last_take_end_index+len(indices)-1  # Compensation for indexation from 0.
                self._positions[column_name][extension_hole] = 1
            last_take_end_index = self._positions.apply(
                lambda series: series.last_valid_index()
            )[column_name]
            take += 1

    def _make_rail_indications(self):
        # Make markings for rail indications.
        rail_indices = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2
        ]
        repetitions = ceil(len(self._positions)/len(rail_indices))
        rail_indices_across_height = repetitions * rail_indices
        self._positions['original_rail_indices'] = \
            rail_indices_across_height[0:len(self._positions)]       
        self._positions['rail_indices'] = \
            rail_indices_across_height[0:len(self._positions)]
        hinge_indication = self._positions['hinge_indication'] == '-'
        slide_indication = self._positions['drawer_indication'] == '-'
        shelve_indication = self._positions['shelf_indication'] == '-'
        divider_indication = \
            self._positions['divider_indication'] == '-'
        markings = np.all([
            hinge_indication, 
            slide_indication, 
            shelve_indication, 
            divider_indication
        ], axis=0)
        self._positions.loc[markings, 'rail_indices'] = '-x-'

    def compute_elevation(self):
        self._create_positions()
        if self.sections:
            self._indicate_sections()
            self._indicate_hinges()
        if self.drawers:
            self._indicate_drawers()
        if self.shelves:
            self._indicate_shelves()  
        if self.dividers:
            self._indicate_dividers()  
        self._make_indications()
    
    def write_elevation(self):
        with pd.ExcelWriter(self.elevation_file) as writer:
            self._positions.to_excel(
                excel_writer=writer, 
                sheet_name='ELEVATION',             
                merge_cells=False
            )

    def get_system_holes(self):
        relevant_column_names = [
            'hinge_indication',
            'drawer_indication',
            'shelf_indication',
            'divider_indication'
        ]
        indication = self._positions.loc[:, relevant_column_names] != '-'
        relevant_rows = np.any(indication, axis=1)

        occupied_positions = \
            self._positions.loc[relevant_rows, relevant_column_names]        

        summary_indication = np.array(np.argwhere(indication))

        labels = []
        for row in range(0, len(summary_indication)):
            current_row = summary_indication[row].tolist()
            labels.append(
                self._positions.iloc[current_row[0], :].loc[relevant_column_names[current_row[1]]]
            )         
        
        return {
            "positions": self._positions.loc[relevant_rows, 1].tolist(),
            "labels": labels
        }
    
    def get_drawers(self):
        relevant_column_names = [
            'drawer_indication'
        ]
        indication = self._positions.loc[:, relevant_column_names] != '-'
        relevant_rows = np.any(indication, axis=1)
        
        return self._positions.loc[relevant_rows, 1].tolist()

    def get_section_indications(self):

        #assert self._section_indications, 'No indications.'

        return self._section_indications


class Elevation:

    def __init__(self, 
                 height: int, 
                 sections: list[int],
                 hinges: list[int],
                 drawers: list[int]) -> None:
        self.height = height
        self.sections = sections
        self.hinges = hinges
        self.drawers = drawers

    def compute_positions(self):
        positions = []

        for position in range(16, self.height, 32):
            positions.extend([position])

        positions_table = pd.DataFrame.from_records(
            [positions, positions[::-1]]
        )
        transposed = positions_table.transpose()
        transposed['skip_indication'] = 'USABLE'
        transposed['hinge_indication'] = 'NO HINGE'
        transposed['drawer_indication'] = 'NO SLIDE'

        if self.height - 16 <= positions[-1]:
            transposed['skip_indication'].iloc[-1] = 'BLOCKED'
            transposed['skip_indication'].iloc[0] = 'BLOCKED'
       
        # Section indication
        zero_padding = [0] + self.sections        
        cumulative_heights = np.cumsum(zero_padding)
        pairs = [
            [cumulative_heights[i], cumulative_heights[i + 1]]
            for i in range(len(cumulative_heights) - 1)
        ]
        dividers = []
        for index, pair in enumerate(pairs):
            section = f"SECTION_{index}_"
            start = pair[0]
            end = pair[1]
            dif_start = start - transposed.iloc[:, 0]
            dif_end = end - transposed.iloc[:, 0]
            start_hinge_1 = dif_start == -16
            start_hinge_2 = dif_start == -48
            end_hinge_1 = dif_end == 48
            end_hinge_2 = dif_end == 16

            transposed.loc[start_hinge_1, 'hinge_indication'] = \
                section + 'TOP_HINGE_1'
            transposed.loc[start_hinge_2, 'hinge_indication'] = \
                section + 'TOP_HINGE_2'
            transposed.loc[end_hinge_1, 'hinge_indication'] = \
                section + 'BOTTOM_HINGE_1'
            transposed.loc[end_hinge_2, 'hinge_indication'] = \
                section + 'BOTTOM_HINGE_2'
            
            # Divider indication.
            dividers.extend([[
                [transposed.loc[start_hinge_1, 1]],
                [transposed.loc[start_hinge_2, 1]],
                [transposed.loc[end_hinge_1, 1]],
                [transposed.loc[end_hinge_2, 1]]    
            ]])

        divs = []
        for index in list(range(0, len(dividers))):
            if index < (len(dividers)-1):
                divs.extend([dividers[index][-1], dividers[index+1][0]])

        for index, (drawers, section) in enumerate(zip(self.drawers, self.sections)):
            if drawers > 0:
                units_per_section = int(section / 32)
                units_per_drawer = int(units_per_section / drawers)
                median_unit = int(np.median(np.arange(1, units_per_drawer+1)))
                indexation = np.arange(
                    median_unit, stop=units_per_section, step=units_per_drawer
                )
                section_start_selection = \
                    transposed.loc[:, 0] == cumulative_heights[index] - 16
                indices = transposed.index[section_start_selection] + indexation
                transposed.loc[indices, 'drawer_indication'] = 'DRAWER_SLIDES'   

        return transposed
    

class ElevationFloorCabinet:

    def __init__(self, height: int, drawers: list[int]) -> None:
        self.height = height
        self.drawers = drawers
        self._positions = None

    def _validate_measurements(self):

        total_drawers = np.sum(self.drawers)

        assert self.height == total_drawers, 'Unequal elevation.'

    def _compute_positions(self):
        positions = []

        for position in range(16, self.height, 32):
            positions.extend([position])

        positions_table = pd.DataFrame.from_records(
            [positions, positions[::-1]]
        )
        self._positions = positions_table.transpose()

    def _add_positioning_column(self):
        self._positions['positioning'] = '-'

    def compute(self):
        self._validate_measurements()
        self._compute_positions()
        self._add_positioning_column()

        if self.height - 16 <= self._positions.iloc[-1, 0]:
            self._positions['positioning'].iloc[-1] = 'BLOCKED'
            self._positions['positioning'].iloc[0] = 'BLOCKED'


        # Section indication
        zero_padding = [0] + self.drawers        
        cumulative_heights = np.cumsum(zero_padding)
        pairs = [
            [cumulative_heights[i], cumulative_heights[i + 1]]
            for i in range(len(cumulative_heights) - 1)
        ]

        for index, (drawer, pair) in enumerate(zip(self.drawers, pairs)):
            #units_per_drawer = drawer / 32
            #median_unit = np.median(np.arange(1, units_per_drawer+1, dtype=int))
            #indexation = pair[0] + (median_unit*32)
            indexation = int(pair[0] + (drawer/2))
            indication = self._positions.iloc[:, 1] == indexation
            indication_sum = np.sum(indication.astype(int))
            if indication_sum > 0:
                self._positions.loc[indication, 'positioning'] = f'DRAWER_{index}'
            if indication_sum == 0:
                indication = self._positions.iloc[:, 1] == (indexation-16)
                self._positions.loc[indication, 'positioning'] = f'DRAWER_{index}_OFF'

    def get_positions(self) -> pd.DataFrame:

        return self._positions



        