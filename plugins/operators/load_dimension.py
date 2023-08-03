from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'
    
    insert_sql = """
        DELETE FROM {};
        INSERT INTO {}
        {};
        COMMIT;
    """
    
    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 table="",
                 load_sql_stmt="",
                 append_only=False,
                 *args, **kwargs):
        
        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.load_sql_stmt = load_sql_stmt
        self.append_only = append_only

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        if not self.append_only:
            self.log.info(f"Loading {self.table} table")
            formatted_sql = LoadDimensionOperator.insert_sql.format(
                self.table,
                self.table,
                self.load_sql_stmt
            )
            redshift.run(formatted_sql)
        if self.append_only:
            self.log.info(f"Loading {self.table} table")
            formatted_sql= "INSERT INTO %s %s" % (self.table, self.load_sql_stmt)
            redshift.run(formatted_sql)