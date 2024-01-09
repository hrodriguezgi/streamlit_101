import os

import pandas as pd
from pandas.io import sql as psql
import snowflake.connector


DF = pd.DataFrame
ColName = str



class Snowflake:
    def __init__(self, database=os.environ['SNOWFLAKE_DATABASE'], db_schema=os.environ['SNOWFLAKE_SCHEMA']) -> None:
        self.user = os.environ['SNOWFLAKE_USER']
        self.password = os.environ['SNOWFLAKE_PASSWORD']
        self.account = os.environ['SNOWFLAKE_ACCOUNT']
        self.warehouse = os.environ['SNOWFLAKE_WAREHOUSE']
        self.role = os.environ['SNOWFLAKE_ROLE']

        engine = snowflake.connector.connect(
            account=self.account,
            user=self.user,
            password=self.password,
            database=database,
            schema=db_schema,
            warehouse=self.warehouse,
            role=self.role,
        )

        try:
            self.connection = engine
        except Exception as err:
            print("I am unable to connect to the database, {}".format(err))
            raise err


    def read_sql(self, sql: str, params=None) -> DF:
        if params is None:
            params = {}

        cs = self.connection.cursor()

        try:
            cs.execute(sql.format(**params))
            self.data = cs.fetch_pandas_all()
        finally:
            cs.close()

        return self.data

    def execute_sp_function(self, function_name, params=[]):
        connection = self.connection
        try:
            cursor = connection.cursor()
            cursor.execute(function_name, params)
            cursor.close()
            connection.commit()
            connection.close()
        except:
            connection.close()
            raise

    def execute_statement(self, sql_statement):
        """
        Executes non result returning statement
        :param sql_statement: sql to execute
        :return: void
        """
        connection = self.connection
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_statement)
        except Exception as e:
            connection.close()
            raise Exception(str(e))

    def set_session(self, tag):
        """
        Set the query tag in the current session
        """
        query_tag = f'ALTER SESSION SET QUERY_TAG = "{tag}"'
        self.execute_statement(query_tag)

    def insert_dataframe_bulk(self, df_to_insert, dest_table, mode, db_schema, flag=False):
        """
        function to save dataframes to tables using snowflake copy clause with parquet files
        this is a slightly modified version of snowflake.connector.pandas with the to_parquet date truncating issue solved
        :param df_to_insert: dataframe to insert
        :param dest_table: name of the table
        :param mode: append,fail or replace
        :param db_schema: schema of the destination table
        :return: None
        """
        if len(df_to_insert) == 0:
            return

        connection = self.connection
        compression = 'gzip'
        compression_map = {
            'gzip': 'auto',
            'snappy': 'snappy'
        }

        # on_error = 'abort_statement'
        stage_name = dest_table.upper()

        path = f'/tmp/{dest_table}.parquet.{compression}'

        if mode == 'replace':
            if flag:
                self.execute_statement(
                    f'drop table if exists {db_schema}.{stage_name}')
                self.execute_statement(pd.io.sql.get_schema(
                    df_to_insert, stage_name).replace('"', ''))
            else:
                """
                ALERT: 2022-06-14
                This function is deprecated because pandas.DataFrame.to_sql use a sqlAlchemy connection
                Always set the flag argument True
                """
                df_to_insert.head(0).to_sql(dest_table.lower(), con=self.connection, index=False, schema=db_schema,
                                            if_exists=mode)

        with connection.cursor() as cursor:
            try:
                # create stage
                try:
                    create_stage_sql = (
                        'create stage {db_schema}.{stage_name}').format(stage_name=stage_name, db_schema=db_schema)
                    cursor.execute(create_stage_sql)
                    connection.commit()
                except Exception as pe:
                    if pe.msg.endswith('already exists.'):
                        pass

                # saves parquet locally
                # using fastparquet because in auto and pyarrow engines datetimes are processed wrong
                # when using auto (default) engine, use these parameters to get the right datetimes in tables:
                # allow_truncated_timestamps=True, use_deprecated_int96_timestamps=True

                df_to_insert.to_parquet(path, engine='auto',  compression=compression, index=False,
                                        allow_truncated_timestamps=True, use_deprecated_int96_timestamps=True)

                # takes local parquet to snowflake stage area .4 parallel processes to load (default)

                upload_sql = ('PUT file://{path} @%{stage_name} PARALLEL={parallel}').format(
                    path=path,
                    stage_name=stage_name,
                    parallel=4
                )
                cursor.execute(upload_sql)
                connection.commit()

                # copy from stage to table
                copy_into_sql = 'COPY INTO {stage_name} MATCH_BY_COLUMN_NAME=CASE_INSENSITIVE ' \
                    'PURGE=TRUE FILE_FORMAT=(TYPE=PARQUET COMPRESSION={compression})'.format(
                        stage_name=stage_name,
                        compression=compression_map[compression])

                cursor.execute(copy_into_sql, _is_internal=True)
                connection.commit()
                os.remove(path)
                #connection.close()

            except Exception as e:
                connection.close()
                raise Exception(e)
