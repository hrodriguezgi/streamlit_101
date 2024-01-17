import duckdb

class MyDuckDB:
    def __init__(self, database) -> None:
        self.conn = duckdb.connect(database=database, read_only=True)


    def get_filter_values(self, column_name):
        return self.conn.execute(f'SELECT DISTINCT {column_name} FROM ANALIZA_IMPORTS ORDER BY 1').df()[f'{column_name}']
    
    def get_filter_date_values(self):
        return self.conn.execute('SELECT MIN(FECHA) AS MIN_DATE, MAX(FECHA) AS MAX_DATE FROM ANALIZA_IMPORTS').df().iloc[0,:]

    def get_metric_values(self, metric, aggregation, **filters):
        if aggregation == 'sum':
            query_metric = f'SELECT SUM({metric}) AS {metric} FROM ANALIZA_IMPORTS WHERE 1=1'
        elif aggregation == 'count':
            query_metric = f'SELECT COUNT({metric}) AS {metric} FROM ANALIZA_IMPORTS WHERE 1=1'
        elif aggregation == 'count_distinct':
            query_metric = f'SELECT COUNT(DISTINCT {metric}) AS {metric} FROM ANALIZA_IMPORTS WHERE 1=1'
        query = (f"""{query_metric}
                 {filters.get('importador', '')}
                 {filters.get('proveedor', '')}
                 {filters.get('pais_origen', '')}
                 {filters.get('pais_procedencia', '')}
                 {filters.get('partida', '')}
                 {filters.get('fecha', '')}
                 """)
        return self.conn.execute(query).df()[f'{metric}']

    def get_total_fob(self, **filters):
        return self.conn.execute(f'''SELECT SUM(FOB) AS TOTAL_FOB
                                 FROM ANALIZA_IMPORTS
                                 WHERE 1=1
                                 {filters.get('importador', '')}
                                 {filters.get('proveedor', '')}
                                 {filters.get('pais_origen', '')}
                                 {filters.get('pais_procedencia', '')}
                                 {filters.get('partida', '')}
                                 {filters.get('fecha')}
                                ''').df().iloc[0,0]


    def get_imports_table(self, category, **filters):
        total_fob = self.conn.execute(f'''
        SELECT SUM(FOB) AS TOTAL_FOB
        FROM ANALIZA_IMPORTS
        WHERE 1=1
        {filters.get('importador', '')}
        {filters.get('proveedor', '')}
        {filters.get('pais_origen', '')}
        {filters.get('pais_procedencia', '')}
        {filters.get('partida', '')}
        {filters.get('fecha')}
        ''').df().iloc[0,0]
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
        FROM ANALIZA_IMPORTS AI
        WHERE 1=1
        {filters.get('importador', '')}
        {filters.get('proveedor', '')}
        {filters.get('pais_origen', '')}
        {filters.get('pais_procedencia', '')}
        {filters.get('partida', '')}
        {filters.get('fecha')}
        GROUP BY {category}, TIPO_UNIDADES
        ORDER BY SUM(FOB) DESC'''
        return self.conn.execute(query).df()


    def get_imports_volume(self, **filters):
        query = f'''
        SELECT
            MES::TEXT AS MES
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
        return self.conn.execute(query).df()

    def get_sharings(self, category, **filters):
        total_fob = self.conn.execute(f'''
        SELECT SUM(FOB) AS TOTAL_FOB
        FROM ANALIZA_IMPORTS
        WHERE 1=1
        {filters.get('importador', '')}
        {filters.get('proveedor', '')}
        {filters.get('pais_origen', '')}
        {filters.get('pais_procedencia', '')}
        {filters.get('partida', '')}
        {filters.get('fecha')}
        ''').df().iloc[0,0]
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
        return self.conn.execute(query).df()