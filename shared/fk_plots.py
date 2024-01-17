import altair as alt

class MyAltair:
    def __init__(self) -> None:
        pass

    def create_altair_importaciones(self, data):
        fig = (alt.Chart(data).mark_area()
               .encode(x=alt.X('MES', sort=None),
                       y=alt.Y('FOB', sort=None),
                       text='MES')
               .interactive()
              )
        return fig

    def create_altair_sharing(self, data, categoria, num_plot):
        chart_data = (data[[f'{categoria}', 'PARTICIPACION']]
                      .sort_values('PARTICIPACION', ascending=False)
                      .drop_duplicates([f'{categoria}'], keep='first')
                      .head(num_plot))
        fig = (alt.Chart(chart_data).mark_bar()
               .encode(x=alt.X('PARTICIPACION', sort=None),
                       y=alt.Y(f'{categoria}', sort=None),
                       text='PARTICIPACION')
               .interactive()
              )
        return fig