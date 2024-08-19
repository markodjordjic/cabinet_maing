import pandas as pd
from cabinet.constructions import Section, Cupboard
from cabinet.measurements import ElevationFloorCabinet


if __name__ == '__main__':

    bottom_section = Section(
        room='Living Room',
        section_name='Documentation Cabinet',
        base_name='Documentation',
        cabinet_type='floor',
        total_units=2,
        height=768,
        width=448,
        depth=608,
        back_tolerance=2,
        drawers=[288, 160, 160, 160],
        top_relief=0
    )

    kitchen_bottom = bottom_section.make_cabinets()

    #complete = pd.concat((kitchen_bottom), axis=0)

    summary = \
        kitchen_bottom.groupby(by=['Materijal', 'Part', 'X', 'Y']).aggregate({
        'Units': sum,
        'Banding': min
    })


    with pd.ExcelWriter('console_material.xlsx') as writer:
        summary.to_excel(excel_writer=writer, sheet_name='MATERIJAL')

    elevation = ElevationFloorCabinet(
        height=768,
        drawers=[288, 160, 160, 160]
    )
    elevation.compute()
    console_elevation = elevation.get_positions()

    with pd.ExcelWriter('console_elevation.xlsx') as writer:
        console_elevation.to_excel(excel_writer=writer, sheet_name='ELEVATION')


    # cupboard_clothes = Cupboard(
    #     height=2208,
    #     width=608,
    #     depth=544,
    #     back_tolerance=3,
    #     h_dividers=2,
    #     drawers=5,
    #     drawer_face_height=800,
    #     front_sections=[256, 1952],
    #     doors_per_section=[1, 1]
    # )
    # cupboard_clothes_material = cupboard_clothes.compute_total_material()

    # cupboard_shelves = Cupboard(
    #     height=2208,
    #     width=608,
    #     depth=544,
    #     back_tolerance=3,
    #     h_dividers=2,
    #     drawers=0,
    #     drawer_face_height=0,
    #     front_sections=[256, 1952],
    #     doors_per_section=[1, 1]
    # )
    # cupboard_shelves_material = cupboard_shelves.compute_total_material()

    # cupboard_hh_items_1 = Cupboard(
    #     height=2208,
    #     width=608,
    #     depth=544,
    #     back_tolerance=3,
    #     h_dividers=2,
    #     drawers=0,
    #     shelves=8,
    #     drawer_face_height=0,
    #     front_sections=[256, 1952],
    #     doors_per_section=[1, 1]
    # )
    # cupboard_hh_items_1_material =  cupboard_hh_items_1.compute_total_material()

    # cupboard_hh_items_2 = Cupboard(
    #     height=2208,
    #     width=608,
    #     depth=544,
    #     back_tolerance=3,
    #     h_dividers=1,
    #     drawers=0,
    #     drawer_face_height=0,
    #     front_sections=[320, 1984],
    #     doors_per_section=[1, 1]
    # )
    # cupboard_hh_items_2_material =  cupboard_hh_items_1.compute_total_material()

    # cupboard_clothes_material.columns = cupboard_shelves_material.columns =\
    #     cupboard_hh_items_1_material.columns = \
    #         cupboard_hh_items_2_material.columns = [
    #             'Materijal', 
    #             'Part', 
    #             'X', 
    #             'Y', 
    #             'Units', 
    #             'Banding'
    #         ]
    
    # total_material = pd.concat((
    #     cupboard_clothes_material,
    #     cupboard_shelves_material,
    #     cupboard_hh_items_1_material,
    #     cupboard_hh_items_2_material
    # ))
    # summary = \
    #     total_material.groupby(by=['Materijal', 'Part', 'X', 'Y']).aggregate({
    #     'Units': sum,
    #     'Banding': min
    # })

    # with pd.ExcelWriter('cupboard.xlsx') as writer:
    #     summary.to_excel(excel_writer=writer, sheet_name='MATERIJAL')

