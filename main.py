import datetime

import streamlit as st
from millify import millify

from shared.snowflake import Snowflake
from queries import analisis_importaciones

st.set_page_config(layout="wide")

db_obj = Snowflake(database='FKPDN_DWH', db_schema='ANALIZA')
datos = db_obj.read_sql(analisis_importaciones)


supplier_list = list(datos['PROVIDER_NAME'].unique())
supplier_list.sort()

importer_list = list(datos['CUSTOMER_NAME'].unique())
importer_list.sort()

country_src_list = list(datos['ORIGIN_COUNTRY'].unique())
country_src_list.sort()

country_pro_list = list(datos['PROVENANCE_COUNTRY'].unique())
country_pro_list.sort()

start_date = datos['IMPORT_DATE'].min()
end_date = datos['IMPORT_DATE'].max()

# FILA 1
with st.container(border=True):
    logo, filters = st.columns((1, 5))
    logo.write('Logo Here!')

    with filters.expander('Filtros'):
        filter1, filter2, filter3, filter4, filter5 = st.columns(5)

        supplier_select = filter1.multiselect('Proveedor',
                                              options=supplier_list,
                                              default=supplier_list)
        importer_select = filter2.multiselect('Importador',
                                              options=importer_list,
                                              default=importer_list)
        country_src_select = filter3.multiselect('Pais de origen de mercancia',
                                                 options=country_src_list,
                                                 default=country_src_list)
        country_pro_select = filter4.multiselect('Pais de origen',
                                                 options=country_pro_list,
                                                 default=country_pro_list)
        
        #dates = filter5.date_input('Fecha importación', start_date, end_date)
        filter5.write('Filtro de fechas')

datos_visualizar = datos[(datos['PROVIDER_NAME'].isin(supplier_select)) &
                         (datos['CUSTOMER_NAME'].isin(importer_select)) &
                         (datos['ORIGIN_COUNTRY'].isin(country_src_select)) &
                         (datos['PROVENANCE_COUNTRY'].isin(country_pro_select))]

# FILA 2
f2c1, f2c2, f2c3, f2c4, f2c5 = st.columns((3, 1, 1, 1, 1))

with f2c1.container(border=True):
    st.write('Posicion arancelaria')


with f2c2.container(border=True):
    fob_metric = round(sum(list(datos_visualizar['FOB_VALUE_USD'])), 2)
    st.metric(label='**FOB**', value=millify(fob_metric, precision=2))

with f2c3.container(border=True):
    cif_metric = round(sum(list(datos_visualizar['CIF_VALUE_USD'])), 2)
    st.metric(label='**CIF**', value=millify(cif_metric, precision=2))

with f2c4.container(border=True):
    weight_metric = round(sum(list(datos_visualizar['NET_WEIGHT_KILOGRAMS'])), 2)
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
        st.write('Otra métrica')

with f3c2.container(border=True):
    st.subheader('Importaciones realizadas')
    # VISUALIZACION DE DATAFRAME
    if categoria == 'Posición arancelaria':
        st.dataframe(
            datos_visualizar[['TARIFF_LEVEL3_DESCRIPTION',
                              'FOB_VALUE_USD',
                              'CIF_VALUE_USD',
                              'UNIT_DESCRIPTION',
                              'QUANTITY_UNITS'
                              ]].sort_values(['FOB_VALUE_USD'], ascending=False),
            hide_index=True)
    elif categoria == 'Importador':
        st.dataframe(
            datos_visualizar[['CUSTOMER_NAME',
                              'FOB_VALUE_USD',
                              'CIF_VALUE_USD',
                              'UNIT_DESCRIPTION',
                              'QUANTITY_UNITS'
                              ]].sort_values(['FOB_VALUE_USD'], ascending=False),
            hide_index=True)
    elif categoria == 'País de origen':
        st.dataframe(
            datos_visualizar[['ORIGIN_COUNTRY',
                              'FOB_VALUE_USD',
                              'CIF_VALUE_USD',
                              'UNIT_DESCRIPTION',
                              'QUANTITY_UNITS'
                              ]].sort_values(['FOB_VALUE_USD'], ascending=False),
            hide_index=True)
    elif categoria == 'Proveedor':
        st.dataframe(
            datos_visualizar[['PROVIDER_NAME',
                              'FOB_VALUE_USD',
                              'CIF_VALUE_USD',
                              'UNIT_DESCRIPTION',
                              'QUANTITY_UNITS'
                              ]].sort_values(['FOB_VALUE_USD'], ascending=False),
            hide_index=True)

with f3c3.container(border=True):
    st.subheader('Volumen de importaciones')
    st.area_chart(datos_visualizar[['IMPORT_DATE', 'FOB_VALUE_USD']].groupby('IMPORT_DATE').sum().sort_values('IMPORT_DATE'))
    st.write('Grafica')

# FILA 4
f4c1, f4c2, f4c3 = st.columns(3)
with f4c1.container(border=True):
    st.write('% participación por importador')

with f4c2.container(border=True):
    st.write('% participación por proveedor')

with f4c3.container(border=True):
    st.write('% participación por pais de procedencia')