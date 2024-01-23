import logging

import streamlit as st
from millify import millify

from shared.fk_duckdb import MyDuckDB
from shared.fk_plots import MyAltair

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

st.set_page_config(layout="wide",
                   page_title='Finkargo Analiza',
                   page_icon='logo.png',
                   menu_items={'About': '''# Finkargo Analiza
                                        Análisis de importaciones Colombianas'''})


def plot_importaciones(data):
    st.dataframe(data,
                 hide_index=True,
                 height=300,
                 use_container_width=True,
                 column_config={'PARTICIPACION': st.column_config.NumberColumn(format='%.2f %%'),
                                'FOB': st.column_config.NumberColumn(format='$ %.2f'),
                                'CIF': st.column_config.NumberColumn(format='$ %.2f'),
                                'FOB_X_UNIDAD': st.column_config.NumberColumn(format='$ %.2f'),
                                'CIF_X_UNIDAD': st.column_config.NumberColumn(format='$ %.2f')}
                )


if __name__ == '__main__':
    db_obj = MyDuckDB('analiza')
    alt = MyAltair()

    tab1, tab2 = st.tabs(['Pag. 1', 'Pag. 2'])
    with tab1:
        st.title('Versión DuckDB')

        supplier_list = db_obj.get_filter_values('PROVEEDOR')
        if 'selected_supplier' not in st.session_state:
            st.session_state['selected_supplier'] = []

        importer_list = db_obj.get_filter_values('IMPORTADOR')
        if 'selected_importer' not in st.session_state:
            st.session_state['selected_importer'] = []

        country_src_list = db_obj.get_filter_values('PAIS_ORIGEN')
        if 'selected_country_src' not in st.session_state:
            st.session_state['selected_country_src'] = []

        country_pro_list = db_obj.get_filter_values('PAIS_PROCEDENCIA')
        if 'selected_country_pro' not in st.session_state:
            st.session_state['selected_country_pro'] = []

        tariff_list = db_obj.get_filter_values('PARTIDA')
        if 'selected_tariff' not in st.session_state:
            st.session_state['selected_tariff'] = []

        min_date, max_date = db_obj.get_filter_date_values()
        #if 'selected_dates' not in st.session_state:
        #    st.session_state['selected_dates'] = (min_date, max_date)


        st.sidebar.image('logo.png')

        with st.sidebar.expander('Fecha importacion', expanded=True):
            st.date_input('Fecha desde',
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key='selected_dates',
                        label_visibility='hidden')
            date_query = f"""AND FECHA BETWEEN '{st.session_state['selected_dates'][0]}' AND '{st.session_state['selected_dates'][1]}'"""

        with st.sidebar.expander('Proveedores'):
            all_suppliers = st.checkbox('Todos los proveedores', value=True)
            if all_suppliers:
                st.multiselect('Proveedores',
                            placeholder='Todos los proveedores han sido seleccionados',
                            options=supplier_list,
                            key='selected_supplier',
                            label_visibility='hidden',
                            disabled=True)
            else:
                st.multiselect('Proveedores',
                            placeholder='Escoja uno o más proveedores',
                            options=supplier_list,
                            key='selected_supplier',
                            label_visibility='hidden',
                            disabled=False)
            if len(st.session_state['selected_supplier']) > 0:
                supplier_query = f"""AND PROVEEDOR IN ('{"', '".join(st.session_state['selected_supplier'])}')"""
            else:
                supplier_query = ''

        with st.sidebar.expander('Importadores'):
            all_importers = st.checkbox('Todos los importadores', value=True)
            if all_importers:
                st.multiselect('Proveedores',
                            placeholder='Todos los importadores han sido seleccionados',
                            options=importer_list,
                            key='selected_importer',
                            label_visibility='hidden',
                            disabled=True)
            else:
                st.multiselect('Proveedores',
                            placeholder='Escoja uno o más importadores',
                            options=importer_list,
                            key='selected_importer',
                            label_visibility='hidden',
                            disabled=False)
            if len(st.session_state['selected_importer']) > 0:
                importer_query = f"""AND IMPORTADOR IN ('{"', '".join(st.session_state['selected_importer'])}')"""
            else:
                importer_query = ''

        with st.sidebar.expander('Pais de origen'):
            all_country_src = st.checkbox('Todos los paises de origen', value=True)
            if all_country_src:
                st.multiselect('Pais origen',
                            placeholder='Todos los paises han sido seleccionados',
                            options=country_src_list,
                            key='selected_country_src',
                            label_visibility='hidden',
                            disabled=True)
            else:
                st.multiselect('Pais origen',
                            placeholder='Escoja uno o más paises',
                            options=country_src_list,
                            key='selected_country_src',
                            label_visibility='hidden',
                            disabled=False)
            if len(st.session_state['selected_country_src']) > 0:
                    country_src_query = f"""AND PAIS_ORIGEN IN ('{"', '".join(st.session_state['selected_country_src'])}')"""
            else:
                country_src_query = ''

        with st.sidebar.expander('Pais de procedencia'):
            all_country_pro = st.checkbox('Todos los paises de procedencia', value=True)
            if all_country_pro:
                st.multiselect('Pais procedencia',
                            placeholder='Todos los paises han sido seleccionados',
                            options=country_src_list,
                            key='selected_country_pro',
                            label_visibility='hidden',
                            disabled=True)
            else:
                st.multiselect('Pais procedencia',
                            placeholder='Escoja uno o más paises',
                            options=country_src_list,
                            key='selected_country_pro',
                            label_visibility='hidden',
                            disabled=False)
            if len(st.session_state['selected_country_pro']) > 0:
                    country_pro_query = f"""AND PAIS_PROCEDENCIA IN ('{"', '".join(st.session_state['selected_country_pro'])}')"""
            else:
                country_pro_query = ''

        with st.sidebar.expander('Partidas arancelarias'):
            all_tariff = st.checkbox('Todas las partidas', value=True)
            if all_tariff:
                st.multiselect('Partidas',
                            placeholder='Todas las partidas han sido seleccionados',
                            options=tariff_list,
                            key='selected_tariff',
                            label_visibility='hidden',
                            disabled=True)
            else:
                st.multiselect('Pais procedencia',
                            placeholder='Escoja una o más partidas',
                            options=tariff_list,
                            key='selected_tariff',
                            label_visibility='hidden',
                            disabled=False)
            if len(st.session_state['selected_tariff']) > 0:
                    tariff_query = f"""AND PARTIDA IN ('{"', '".join(st.session_state['selected_tariff'])}')"""
            else:
                tariff_query = ''



        # FILA 1: METRICAS
        f2c1, f2c2, f2c3, f2c4, f2c5 = st.columns(5)

        with f2c1.container(border=True):
            fob_metric = db_obj.get_metric_values('FOB',
                                                'sum',
                                                proveedor=supplier_query,
                                                importador=importer_query,
                                                pais_origen=country_src_query,
                                                pais_procedencia=country_pro_query,
                                                partida=tariff_query,
                                                fecha=date_query)
            st.metric(label='**FOB**', value='{:0,.2f}'.format(fob_metric.iloc[0]))

        with f2c2.container(border=True):
            cif_metric = db_obj.get_metric_values('CIF',
                                                'sum',
                                                proveedor=supplier_query,
                                                importador=importer_query,
                                                pais_origen=country_src_query,
                                                pais_procedencia=country_pro_query,
                                                partida=tariff_query,
                                                fecha=date_query)
            st.metric(label='**CIF**', value=cif_metric)

        with f2c3.container(border=True):
            peso_metric = db_obj.get_metric_values('PESO_NETO',
                                                'sum',
                                                proveedor=supplier_query,
                                                importador=importer_query,
                                                pais_origen=country_src_query,
                                                pais_procedencia=country_pro_query,
                                                partida=tariff_query,
                                                fecha=date_query)
            st.metric(label='**Peso neto**', value=peso_metric)

        with f2c4.container(border=True):
            partidas_metric = db_obj.get_metric_values('PARTIDA',
                                                    'count_distinct',
                                                    proveedor=supplier_query,
                                                    importador=importer_query,
                                                    pais_origen=country_src_query,
                                                    pais_procedencia=country_pro_query,
                                                    partida=tariff_query,
                                                    fecha=date_query)
            st.metric(label='**# partidas**', value=partidas_metric)

        with f2c5.container(border=True):
            operaciones_metric = db_obj.get_metric_values('PARTIDA',
                                                        'count',
                                                        proveedor=supplier_query,
                                                        importador=importer_query,
                                                        pais_origen=country_src_query,
                                                        pais_procedencia=country_pro_query,
                                                        partida=tariff_query,
                                                        fecha=date_query)
            st.metric(label='**Operaciones**', value=operaciones_metric)



        # FILA 2: GRAFICAS
        f3c1, f3c2 = st.columns((4, 2))

        with f3c1.container(border=True):
            st.write('##### Importaciones realizadas')
            categoria = st.radio(label='Seleccione una categoria',
                                    options=['Posición arancelaria',
                                            'Importador',
                                            'País de origen',
                                            'Proveedor'
                                            ],
                                    index=0,
                                    horizontal=True)

            # VISUALIZACION DE DATAFRAME
            if categoria == 'Posición arancelaria':
                datos_tabla = db_obj.get_imports_table('PARTIDA',
                                                    proveedor=supplier_query,
                                                    importador=importer_query,
                                                    pais_origen=country_src_query,
                                                    pais_procedencia=country_pro_query,
                                                    partida=tariff_query,
                                                    fecha=date_query)
                plot_importaciones(datos_tabla)
            elif categoria == 'Importador':
                datos_tabla = db_obj.get_imports_table('IMPORTADOR',
                                                    proveedor=supplier_query,
                                                    importador=importer_query,
                                                    pais_origen=country_src_query,
                                                    pais_procedencia=country_pro_query,
                                                    partida=tariff_query,
                                                    fecha=date_query)
                plot_importaciones(datos_tabla)
            elif categoria == 'País de origen':
                datos_tabla = db_obj.get_imports_table('PAIS_ORIGEN',
                                                    proveedor=supplier_query,
                                                    importador=importer_query,
                                                    pais_origen=country_src_query,
                                                    pais_procedencia=country_pro_query,
                                                    partida=tariff_query,
                                                    fecha=date_query)
                plot_importaciones(datos_tabla)
            elif categoria == 'Proveedor':
                datos_tabla = db_obj.get_imports_table('PROVEEDOR',
                                                    proveedor=supplier_query,
                                                    importador=importer_query,
                                                    pais_origen=country_src_query,
                                                    pais_procedencia=country_pro_query,
                                                    partida=tariff_query,
                                                    fecha=date_query)
                plot_importaciones(datos_tabla)

        with f3c2.container(border=True):
            st.write('##### Volumen de importaciones')
            datos_grafica = db_obj.get_imports_volume(proveedor=supplier_query,
                                                    importador=importer_query,
                                                    pais_origen=country_src_query,
                                                    pais_procedencia=country_pro_query,
                                                    partida=tariff_query,
                                                    fecha=date_query)
            datos_grafica['MES'] = datos_grafica['MES'].apply(lambda x: str(x))
            c = alt.create_altair_importaciones(datos_grafica)
            st.altair_chart(c, theme='streamlit', use_container_width=True)



        # FILA 3: GRACIAS
        f4c1, f4c2, f4c3 = st.columns(3)

        with f4c1.container(border=True):
            participacion_importador = db_obj.get_sharings('IMPORTADOR',
                                                        proveedor=supplier_query,
                                                        importador=importer_query,
                                                        pais_origen=country_src_query,
                                                        pais_procedencia=country_pro_query,
                                                        partida=tariff_query,
                                                        fecha=date_query)
            default_value = 15 if participacion_importador.shape[0] > 15 else participacion_importador.shape[0]
            st.write('##### % participación por importador')
            num_impo_plot = st.number_input('Importadores a visualizar',
                                            min_value=1,
                                            max_value=participacion_importador.shape[0],
                                            value=default_value,
                                            step=5)
            c = alt.create_altair_sharing(participacion_importador, 'IMPORTADOR', num_impo_plot)
            st.altair_chart(c, theme='streamlit', use_container_width=True)

        with f4c2.container(border=True):
            participacion_proveedor = db_obj.get_sharings('PROVEEDOR',
                                                        proveedor=supplier_query,
                                                        importador=importer_query,
                                                        pais_origen=country_src_query,
                                                        pais_procedencia=country_pro_query,
                                                        partida=tariff_query,
                                                        fecha=date_query)
            default_value = 15 if participacion_proveedor.shape[0] > 15 else participacion_proveedor.shape[0]
            st.write('##### % participación por proveedor')
            num_prov_plot = st.number_input('Proveedores a visualizar',
                                            min_value=1,
                                            max_value=participacion_proveedor.shape[0],
                                            value=default_value,
                                            step=5)
            c = alt.create_altair_sharing(participacion_proveedor, 'PROVEEDOR', num_prov_plot)
            st.altair_chart(c, theme='streamlit', use_container_width=True)

        with f4c3.container(border=True):
            participacion_pais = db_obj.get_sharings('PAIS_ORIGEN',
                                                    proveedor=supplier_query,
                                                    importador=importer_query,
                                                    pais_origen=country_src_query,
                                                    pais_procedencia=country_pro_query,
                                                    partida=tariff_query,
                                                    fecha=date_query)
            default_value = 15 if participacion_pais.shape[0] > 15 else participacion_pais.shape[0]
            st.write('##### % participación por pais de procedencia')
            num_country_plot = st.number_input('Países a visualizar',
                                        min_value=1,
                                        max_value=participacion_pais.shape[0],
                                        value=default_value,
                                        step=5)
            c = alt.create_altair_sharing(participacion_pais, 'PAIS_ORIGEN', num_country_plot)
            st.altair_chart(c, theme='streamlit', use_container_width=True)

    with tab2:
        datos_tabla = db_obj.get_imports_table('PARTIDA',
                                                    proveedor=supplier_query,
                                                    importador=importer_query,
                                                    pais_origen=country_src_query,
                                                    pais_procedencia=country_pro_query,
                                                    partida=tariff_query,
                                                    fecha=date_query)
        plot_importaciones(datos_tabla)