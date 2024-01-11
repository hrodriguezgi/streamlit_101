import streamlit as st
from millify import millify
import plotly.express as px

from shared.snowflake import Snowflake
from queries import analisis_importaciones

st.set_page_config(layout="wide",
                   page_title='Finkargo Analiza',
                   page_icon='logo.png',
                   menu_items={'About': '# Finkargo Analiza'})


@st.cache_data
def get_data():
    db_obj = Snowflake(database='FKPDN_DWH', db_schema='ANALIZA')
    return db_obj.read_sql(analisis_importaciones)


datos = get_data()


supplier_list = list(datos['PROVEEDOR'].unique())
supplier_list.sort()

importer_list = list(datos['IMPORTADOR'].unique())
importer_list.sort()

country_src_list = list(datos['PAIS_ORIGEN'].unique())
country_src_list.sort()

country_pro_list = list(datos['PAIS_PROCEDENCIA'].unique())
country_pro_list.sort()

start_date = datos['FECHA'].min()
end_date = datos['FECHA'].max()

tariff_list = list(datos['PARTIDA'].unique())
tariff_list.sort()


# FILA 1
f1c1, f1c2, f1c3, f1c4, f1c5, f1c6, f1c7 = st.columns((0.3,1,1,1,1,1,1))

f1c1.image('logo.png')

with f1c2.expander('Proveedor'):
    all_supplier = st.checkbox('Todos los proveedores', value=True)
    if all_supplier:
        supplier_select = st.multiselect(label='Todos los proveedores',
                                         options=supplier_list,
                                         default=supplier_list,
                                         label_visibility='hidden')
    else:
        supplier_select = st.multiselect(label='Todos los proveedores',
                                         options=supplier_list,
                                         label_visibility='hidden')

with f1c3.expander('Importador'):
    all_importer = st.checkbox('Todos los importadores', value=True)
    if all_importer:
        importer_select = st.multiselect(label='Todos los importadores',
                                         options=importer_list,
                                         default=importer_list,
                                         label_visibility='hidden')
    else:
        importer_select = st.multiselect(label='Todos los importadores',
                                         options=importer_list,
                                         label_visibility='hidden')

with f1c4.expander('Pais de origen de mercancia'):
    all_src_country = st.checkbox('Todos los paises de origen', value=True)
    if all_src_country:
        country_src_select = st.multiselect('Todos los paises de origen',
                                            options=country_src_list,
                                            default=country_src_list,
                                            label_visibility='hidden')
    else:
        country_src_select = st.multiselect('Todos los paises de origen',
                                            options=country_src_list,
                                            label_visibility='hidden')

with f1c5.expander('Pais de procedencia'):
    all_pro_country = st.checkbox('Todos los paises de procedencia', value=True)
    if all_pro_country:
        country_pro_select = st.multiselect('Todos los paises de procedencia',
                                            options=country_pro_list,
                                            default=country_pro_list,
                                            label_visibility='hidden')
    else:
        country_pro_select = st.multiselect('Todos los paises de procedencia',
                                            options=country_pro_list,
                                            label_visibility='hidden')

with f1c6.expander('Fecha de importacion'):
    dates = st.date_input('Fecha de importacion',
                          (start_date, end_date),
                          min_value=start_date,
                          max_value=end_date,
                          label_visibility='hidden')

with f1c7.expander('Posición arancelaria'):
    all_tariff = st.checkbox('Todas las posiciones arancelarias', value=True)
    if all_tariff:
        tariff_select = st.multiselect('Todas las posiciones arancelarias',
                                       options=tariff_list,
                                       default=tariff_list,
                                       label_visibility='hidden')
    else:
        tariff_select = st.multiselect('Todas las posiciones arancelarias',
                                       options=tariff_list,
                                       label_visibility='hidden')

datos_visualizar = datos[(datos['PROVEEDOR'].isin(supplier_select)) &
                         (datos['IMPORTADOR'].isin(importer_select)) &
                         (datos['PAIS_ORIGEN'].isin(country_src_select)) &
                         (datos['PAIS_PROCEDENCIA'].isin(country_pro_select)) &
                         (datos['PARTIDA'].isin(tariff_select)) &
                         (datos['FECHA'] >= dates[0]) & (datos['FECHA'] <= dates[1])]

# FILA 2
f2c1, f2c2, f2c3, f2c4, f2c5 = st.columns(5)

with f2c1.container(border=True):
    fob_metric = round(datos_visualizar['FOB'].sum(), 2)
    st.metric(label='**FOB**', value=millify(fob_metric, precision=2))

with f2c2.container(border=True):
    cif_metric = round(datos_visualizar['CIF'].sum(), 2)
    st.metric(label='**CIF**', value=millify(cif_metric, precision=2))

with f2c3.container(border=True):
    weight_metric = round(datos_visualizar['PESO_NETO'].sum(), 2)
    st.metric(label='**Peso neto (Kg)**', value=millify(weight_metric, precision=2))

with f2c4.container(border=True):
    partidas = len(datos_visualizar['PARTIDA'].unique())
    st.metric(label='**# Partidas**', value=partidas)

with f2c5.container(border=True):
    operations = datos_visualizar.shape[0]
    st.metric(label='**Operaciones**', value=operations)


# FILA 3
f3c1, f3c2 = st.columns((4, 2))

with f3c1.container(border=True):
    st.write('#### Importaciones realizadas')
    categoria = st.radio(label='Seleccione una categoria',
                            options=['Posición arancelaria',
                                    'Importador',
                                    'País de origen',
                                    'Proveedor'
                                    ],
                            index=0,
                            horizontal=True)

    @st.cache_data
    def get_importaciones(datos, categoria):
        datos_resultado = datos[[f'{categoria}', 'FOB', 'CIF', 'TIPO_UNIDADES', 'UNIDADES']]\
                            .groupby([f'{categoria}', 'TIPO_UNIDADES'])\
                            .sum()\
                            .reset_index()\
                            .sort_values(['FOB'], ascending=False)
        datos_resultado['FOB_X_UNIDAD'] = datos_resultado['FOB']/datos_resultado['UNIDADES']
        datos_resultado['CIF_X_UNIDAD'] = datos_resultado['CIF']/datos_resultado['UNIDADES']
        total_fob = datos_resultado['FOB'].sum()
        datos_resultado['PARTICIPACION'] = round(datos_resultado['FOB']/total_fob * 100, 2)
        datos_resultado = datos_resultado[[f'{categoria}',
                                           'PARTICIPACION',
                                           'FOB',
                                           'CIF',
                                           'TIPO_UNIDADES',
                                           'UNIDADES',
                                           'FOB_X_UNIDAD',
                                           'CIF_X_UNIDAD']]
        return datos_resultado

    def plot_importaciones(datos):
        st.dataframe(datos_tabla,
                     hide_index=True,
                     height=380,
                     use_container_width=True,
                     column_config={'PARTICIPACION': st.column_config.NumberColumn(format='%.2f %%'),
                                    'FOB': st.column_config.NumberColumn(format='$ %.2f'),
                                    'CIF': st.column_config.NumberColumn(format='$ %.2f'),
                                    'FOB_X_UNIDAD': st.column_config.NumberColumn(format='$ %.2f'),
                                    'CIF_X_UNIDAD': st.column_config.NumberColumn(format='$ %.2f')})

    # VISUALIZACION DE DATAFRAME
    if categoria == 'Posición arancelaria':
        datos_tabla = get_importaciones(datos_visualizar, 'PARTIDA')
        plot_importaciones(datos_tabla)
    elif categoria == 'Importador':
        datos_tabla = get_importaciones(datos_visualizar, 'IMPORTADOR')
        plot_importaciones(datos_tabla)
    elif categoria == 'País de origen':
        datos_tabla = get_importaciones(datos_visualizar, 'PAIS_ORIGEN')
        plot_importaciones(datos_tabla)
    elif categoria == 'Proveedor':
        datos_tabla = get_importaciones(datos_visualizar, 'PROVEEDOR')
        plot_importaciones(datos_tabla)

with f3c2.container(border=True):
    st.write('#### Volumen de importaciones')
    fig = px.area(datos_visualizar[['MES', 'FOB']].groupby(['MES']).sum().sort_values(['MES']),
                  width = 400,
                  height = 450,
                  markers = True)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)


# FILA 4
f4c1, f4c2, f4c3 = st.columns(3)

@st.cache_data
def get_participacion(data, categoria):
    datos_resultado = data[[f'{categoria}', 'FOB']]\
                        .groupby([f'{categoria}'])\
                        .sum()\
                        .reset_index()\
                        .sort_values(['FOB'], ascending=True)
    total_fob = datos_resultado['FOB'].sum()
    datos_resultado['PARTICIPACION'] = round(datos_resultado['FOB']/total_fob, 4)
    datos_resultado[f'{categoria} '] = datos_resultado[f'{categoria}'].str[:15] + '...'
    return datos_resultado

def plot_participacion(data, categoria):
    fig = px.bar(data,
                 y = f'{categoria} ',
                 x = 'PARTICIPACION',
                 orientation = 'h',
                 width = 400,
                 height = 400,
                 text_auto = '.2%',
                 hover_data = [f'{categoria}', 'PARTICIPACION'])
    return fig

with f4c1.container(border=True):
    participacion_importador = get_participacion(datos_visualizar, 'IMPORTADOR')
    st.write('#### % participación por importador')
    num_impo_plot = st.slider('Importadores a visualizar',
                              min_value=1,
                              max_value=participacion_importador.shape[0],
                              value=10,
                              step=1)
    fig = plot_participacion(participacion_importador.tail(num_impo_plot), 'IMPORTADOR')
    st.plotly_chart(fig)


with f4c2.container(border=True):
    participacion_proveedor = get_participacion(datos_visualizar, 'PROVEEDOR')
    st.write('#### % participación por proveedor')
    num_prov_plot = st.slider('Proveedores a visualizar',
                              min_value=1,
                              max_value=participacion_proveedor.shape[0],
                              value=10,
                              step=1)
    fig = plot_participacion(participacion_proveedor.tail(num_prov_plot), 'PROVEEDOR')
    st.plotly_chart(fig)


with f4c3.container(border=True):
    participacion_pais = get_participacion(datos_visualizar, 'PAIS_PROCEDENCIA')
    st.write('#### % participación por pais de procedencia')
    num_country_plot = st.slider('Países a visualizar',
                                 min_value=1,
                                 max_value=participacion_pais.shape[0],
                                 value=10,
                                 step=1)
    fig = plot_participacion(participacion_pais.tail(num_country_plot), 'PAIS_PROCEDENCIA')
    st.plotly_chart(fig)