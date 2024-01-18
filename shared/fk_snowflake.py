import os

from snowflake.snowpark import Session

class MySnowpark:
    def __init__(self) -> None:
        self.connection_parameters = {
            'user': os.environ['SNOWFLAKE_USER'],
            'password': os.environ['SNOWFLAKE_PASSWORD'],
            'account': os.environ['SNOWFLAKE_ACCOUNT'],
            'role': os.environ['SNOWFLAKE_ROLE'],
            'warehouse': os.environ['SNOWFLAKE_WAREHOUSE'],
            'database': os.environ['SNOWFLAKE_DATABASE'],,
            'schema': os.environ['SNOWFLAKE_SCHEMA'],}
        self.session = Session.builder.configs(self.connection_parameters).create()

    def get_filter_values(self, column_name):
        return [ i[f'{column_name}'] for i in self.session.sql(f'SELECT DISTINCT {column_name} FROM ANALIZA.ANALIZA_IMPORTS ORDER BY 1').collect() ]
    
    def get_filter_date_values(self):
        dates = self.session.sql('SELECT MIN(FECHA) AS MIN_DATE, MAX(FECHA) AS MAX_DATE FROM ANALIZA.ANALIZA_IMPORTS').collect()
        return dates[0]['MIN_DATE'], dates[0]['MAX_DATE']

    def get_metric_values(self, metric, aggregation, **filters):
        if aggregation == 'sum':
            query_metric = f'SELECT SUM({metric}) AS {metric} FROM ANALIZA.ANALIZA_IMPORTS WHERE 1=1'
        elif aggregation == 'count':
            query_metric = f'SELECT COUNT({metric}) AS {metric} FROM ANALIZA.ANALIZA_IMPORTS WHERE 1=1'
        elif aggregation == 'count_distinct':
            query_metric = f'SELECT COUNT(DISTINCT {metric}) AS {metric} FROM ANALIZA.ANALIZA_IMPORTS WHERE 1=1'
        query = (f"""{query_metric}
                 {filters.get('importador', '')}
                 {filters.get('proveedor', '')}
                 {filters.get('pais_origen', '')}
                 {filters.get('pais_procedencia', '')}
                 {filters.get('partida', '')}
                 {filters.get('fecha', '')}
                 """)
        return float(self.session.sql(query).collect()[0][f'{metric}'])

    def get_total_fob(self, **filters):
        return self.session.sql(f'''SELECT SUM(FOB) AS TOTAL_FOB
                                FROM ANALIZA_IMPORTS
                                WHERE 1=1
                                {filters.get('importador', '')}
                                {filters.get('proveedor', '')}
                                {filters.get('pais_origen', '')}
                                {filters.get('pais_procedencia', '')}
                                {filters.get('partida', '')}
                                {filters.get('fecha')}
                                ''').collect().iloc[0,0]


    def get_imports_table(self, category, **filters):
        total_fob = float(self.session.sql(f'''
        SELECT SUM(FOB) AS TOTAL_FOB
        FROM ANALIZA_IMPORTS
        WHERE 1=1
        {filters.get('importador', '')}
        {filters.get('proveedor', '')}
        {filters.get('pais_origen', '')}
        {filters.get('pais_procedencia', '')}
        {filters.get('partida', '')}
        {filters.get('fecha')}
        ''').collect()[0]['TOTAL_FOB'])
        query = f'''
        SELECT
            {category}
            ,SUM(FOB)/{total_fob} * 100 AS PARTICIPACION
            ,SUM(FOB) AS FOB
            ,SUM(CIF) AS CIF
            ,TIPO_UNIDADES
            ,SUM(UNIDADES) AS UNIDADES
            ,SUM(FOB)/SUM(UNIDADES) AS FOB_X_UNIDAD
            ,SUM(CIF)/SUM(UNIDADES) AS CIF_X_UNIDAD
        FROM ANALIZA_IMPORTS
        WHERE 1=1
        {filters.get('importador', '')}
        {filters.get('proveedor', '')}
        {filters.get('pais_origen', '')}
        {filters.get('pais_procedencia', '')}
        {filters.get('partida', '')}
        {filters.get('fecha')}
        GROUP BY {category}, TIPO_UNIDADES
        ORDER BY 3 DESC'''
        return self.session.sql(query).collect()


    def get_imports_volume(self, **filters):
        query = f'''
        SELECT
             MES
            ,SUM(FOB) AS FOB
        FROM ANALIZA_IMPORTS
        WHERE 1=1
        {filters.get('importador', '')}
        {filters.get('proveedor', '')}
        {filters.get('pais_origen', '')}
        {filters.get('pais_procedencia', '')}
        {filters.get('partida', '')}
        {filters.get('fecha')}
        GROUP BY MES
        ORDER BY MES'''
        return self.session.sql(query).toPandas()

    def get_sharings(self, category, **filters):
        total_fob = float(self.session.sql(f'''
        SELECT SUM(FOB) AS TOTAL_FOB
        FROM ANALIZA_IMPORTS
        WHERE 1=1
        {filters.get('importador', '')}
        {filters.get('proveedor', '')}
        {filters.get('pais_origen', '')}
        {filters.get('pais_procedencia', '')}
        {filters.get('partida', '')}
        {filters.get('fecha')}
        ''').collect()[0]['TOTAL_FOB'])
        query = f'''
        SELECT
            {category}
            ,SUM(FOB)/{total_fob} * 100 AS PARTICIPACION
        FROM ANALIZA_IMPORTS
        WHERE 1=1
        {filters.get('importador', '')}
        {filters.get('proveedor', '')}
        {filters.get('pais_origen', '')}
        {filters.get('pais_procedencia', '')}
        {filters.get('partida', '')}
        {filters.get('fecha')}
        GROUP BY 1
        ORDER BY SUM(FOB) DESC'''
        return self.session.sql(query).toPandas()