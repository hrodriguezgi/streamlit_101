import streamlit as st

from shared.snowflake import Snowflake


db_obj = Snowflake(database='FKPDN_DWH', db_schema='ANALIZA')
datos = db_obj.read_sql('SELECT * FROM ANALIZA.ANALIZA_IMPORTS_SOURCE LIMIT 20')


supplier_list = list(datos['PROVIDER_NAME'].unique())
supplier_select = st.multiselect('Proveedor', options=supplier_list, default=supplier_list)

importer_list = list(datos['CUSTOMER_NAME'].unique())
importer_select = st.multiselect('Importador', options=importer_list, default=importer_list)

country_list = list(datos['PROVENANCE_COUNTRY'].unique())
country_select = st.multiselect('Pais de origen de mercancia', options=country_list, default=country_list)

datos_visualizar = datos[(datos['PROVIDER_NAME'].isin(supplier_select)) & (datos['CUSTOMER_NAME'].isin(importer_select)) & (datos['PROVENANCE_COUNTRY'].isin(country_select))]


# VISUALIZACION DE METRICAS
fob_metric = round(sum(list(datos_visualizar['FOB_VALUE_USD'])), 2)
st.metric(label='**FOB**', value=fob_metric,)

cif_metric = round(sum(list(datos_visualizar['CIF_VALUE_USD'])), 2)
st.metric(label='**CIF**', value=cif_metric)

partidas = datos_visualizar.shape[0]
st.metric(label='# Partidas', value=partidas)


# VISUALIZACION DE DATAFRAME
st.dataframe(datos_visualizar[['TARIFF_LEVEL3_DESCRIPTION', 'FOB_VALUE_USD', 'CIF_VALUE_USD', 'UNIT_DESCRIPTION', 'QUANTITY_UNITS']], hide_index=True)