import streamlit as st
from millify import millify

from shared.snowflake import Snowflake
from queries import analisis_importaciones

st.set_page_config(layout="wide")


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



# FILA 1
f1c1, f1c2, f1c3, f1c4, f1c5, f1c6 = st.columns((0.3,1,1,1,1,1))

f1c1.image('logo.png')

with f1c2.expander('Proveedor'):
    all_supplier = st.checkbox('Todos los proveedores', value=True)
    if all_supplier:
        supplier_select = st.multiselect(label='',
                                         options=supplier_list,
                                         default=supplier_list)
    else:
        supplier_select = st.multiselect(label='',
                                         options=supplier_list)

with f1c3.expander('Importador'):
    all_importer = st.checkbox('Todos los importadores', value=True)
    if all_importer:
        importer_select = st.multiselect(label='',
                                         options=importer_list,
                                         default=importer_list)
    else:
        importer_select = st.multiselect(label='',
                                         options=importer_list)

with f1c4.expander('Pais de origen de mercancia'):
    all_src_country = st.checkbox('Todos los paises de origen', value=True)
    if all_src_country:
        country_src_select = st.multiselect('Pais de origen de mercancia',
                                            options=country_src_list,
                                            default=country_src_list)
    else:
        country_src_select = st.multiselect('Pais de origen de mercancia',
                                            options=country_src_list)

with f1c5.expander('Pais de procedencia'):
    all_pro_country = st.checkbox('Todos los paises de procedencia', value=True)
    if all_pro_country:
        country_pro_select = st.multiselect('Pais de origen',
                                            options=country_pro_list,
                                            default=country_pro_list)
    else:
        country_pro_select = st.multiselect('Pais de origen',
                                            options=country_pro_list)
        
with f1c6.expander('Fecha de importacion'):
    st.write('Fecha de importacion')
    dates = st.date_input('Fecha importación')
    st.write(f'{dates}')

datos_visualizar = datos[(datos['PROVEEDOR'].isin(supplier_select)) &
                         (datos['IMPORTADOR'].isin(importer_select)) &
                         (datos['PAIS_ORIGEN'].isin(country_src_select)) &
                         (datos['PAIS_PROCEDENCIA'].isin(country_pro_select))]

# FILA 2
f2c1, f2c2, f2c3, f2c4, f2c5 = st.columns((3, 1, 1, 1, 1))

with f2c1.container(border=True):
    st.write('Posicion arancelaria')


with f2c2.container(border=True):
    fob_metric = round(datos_visualizar['FOB'].sum(), 2)
    st.metric(label='**FOB**', value=millify(fob_metric, precision=2))

with f2c3.container(border=True):
    cif_metric = round(datos_visualizar['CIF'].sum(), 2)
    st.metric(label='**CIF**', value=millify(cif_metric, precision=2))

with f2c4.container(border=True):
    weight_metric = round(datos_visualizar['PESO_NETO'].sum(), 2)
    st.metric(label='**Peso neto (Kg)**', value=millify(weight_metric, precision=2))

with f2c5.container(border=True):
    partidas = datos_visualizar.shape[0]
    st.metric(label='**# Partidas**', value=partidas)


# FILA 3
f3c1, f3c2, f3c3 = st.columns((1, 3, 2))
with f3c1.container():
    with st.container(border=True):
        categoria = st.radio(label='Seleccione una categoria',
                             options=['Posición arancelaria',
                                      'Importador',
                                      'País de origen',
                                      'Proveedor'
                                      ],
                             index=0)

    with st.container(border=True):
        st.write('Operaciones')

with f3c2.container(border=True):
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


    st.subheader('Importaciones realizadas')
    # VISUALIZACION DE DATAFRAME
    if categoria == 'Posición arancelaria':
        datos_tabla = get_importaciones(datos_visualizar, 'PARTIDA')
        st.dataframe(datos_tabla, hide_index=True)
    elif categoria == 'Importador':
        datos_tabla = get_importaciones(datos_visualizar, 'IMPORTADOR')
        st.dataframe(datos_tabla, hide_index=True)
    elif categoria == 'País de origen':
        datos_tabla = get_importaciones(datos_visualizar, 'PAIS_ORIGEN')
        st.dataframe(datos_tabla, hide_index=True)
    elif categoria == 'Proveedor':
        datos_tabla = get_importaciones(datos_visualizar, 'PROVEEDOR')
        st.dataframe(datos_tabla, hide_index=True)

with f3c3.container(border=True):
    st.subheader('Volumen de importaciones')
    st.area_chart(datos_visualizar[['MES', 'FOB']].groupby(['MES']).sum().sort_values(['MES']))


# FILA 4
f4c1, f4c2, f4c3 = st.columns(3)

def get_participacion(datos, categoria):
    datos_resultado = datos[[f'{categoria}']].groupby([f'{categoria}']).agg({f'{categoria}': 'count'}).rename(columns={f'{categoria}':'REGISTROS'}).reset_index()
    datos_resultado['PARTICIPACION'] = round(datos_resultado['REGISTROS']/datos.shape[0] * 100, 2)
    return datos_resultado[[f'{categoria}', 'PARTICIPACION']].sort_values(['PARTICIPACION'], ascending=False)

with f4c1.container(border=True):
    participacion_importador = get_participacion(datos_visualizar, 'IMPORTADOR')
    st.write('% participación por importador')
    st.dataframe(participacion_importador, hide_index=True)


with f4c2.container(border=True):
    participacion_proveedor = get_participacion(datos_visualizar, 'PROVEEDOR')
    st.write('% participación por proveedor')
    st.dataframe(participacion_proveedor, hide_index=True)

with f4c3.container(border=True):
    participacion_pais = get_participacion(datos_visualizar, 'PAIS_PROCEDENCIA')
    st.write('% participación por pais de procedencia')
    st.dataframe(participacion_pais, hide_index=True)