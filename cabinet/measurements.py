import pandas as pd
import numpy as np


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
        # Section indication
        zero_padding = [0] + self.drawers        
        cumulative_heights = np.cumsum(zero_padding)
        pairs = [
            [cumulative_heights[i], cumulative_heights[i + 1]]
            for i in range(len(cumulative_heights) - 1)
        ]

        for index, (drawer, pair) in enumerate(zip(self.drawers, pairs)):
            units_per_drawer = int(drawer / 32)
            median_unit = int(np.median(np.arange(1, units_per_drawer+1)))
            indexation = pair[0] + (median_unit*32)
            indication = self._positions.iloc[:, 1] == indexation
            indication_sum = np.sum(indication.astype(int))
            if indication_sum > 0:
                self._positions.loc[indication, 'positioning'] = f'DRAWER_{index}'
            if indication_sum == 0:
                indication = self._positions.iloc[:, 1] == (indexation-16)
                self._positions.loc[indication, 'positioning'] = f'DRAWER_{index}_OFF'

        print('Finished.')   



        