import pandas as pd
from cabinet.cabinet import Section


if __name__ == '__main__':

    top_section = Section(
        room='Kitchen',
        section_name='Top',
        base_name='Right',
        total_units=5,
        height=800,
        width=448,
        depth=608,
        shelves=2,
        top='one_piece',
        doors=1,
        back_tolerance=2,
        cabinet_type='top'
    )

    kitchen_top = top_section.make_cabinets()

    bottom_section = Section(
        room='Kitchen',
        section_name='Bottom',
        base_name='Right',
        total_units=5,
        height=800,
        width=448,
        depth=608,
        top='two_piece',
        back_tolerance=2,
        drawers=3,
        cabinet_type='bottom_drawers'
    )

    kitchen_bottom = bottom_section.make_cabinets()


    complete = pd.concat((kitchen_top, kitchen_bottom), axis=0)

    summary = \
        complete.groupby(by=['Materijal', 'Part', 'X', 'Y']).aggregate({
        'Units': sum,
        'Banding': min
    })


    with pd.ExcelWriter('materijal.xlsx') as writer:
        summary.to_excel(excel_writer=writer, sheet_name='MATERIJAL')
