import pandas as pd
from cabinet.cabinet import Section


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
        back_tolerance=2,
        drawers=5
    )

    kitchen_top = section.make_cabinets()

    summary = kitchen_top.groupby(by=['Materijal', 'Part', 'X', 'Y']).aggregate({
        'Units': sum,
        'Banding': min
    })

    with pd.ExcelWriter('materijal.xlsx') as writer:
        summary.to_excel(excel_writer=writer, sheet_name='MATERIJAL', )
