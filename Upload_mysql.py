from sqlalchemy import create_engine
import pymysql

class upload_mysql():

    def __init__(self, table_name) -> None:
        """
        If mysql is not launched, run the following scripts:
        mysql -u root
        """
        self.sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/face_to_monitor_distance', \
                        pool_recycle=3600)
        self.dbConnection = self.sqlEngine.connect()

        self.table_name = table_name

        self.table_existence = self._table_existence()

        if not self.table_existence:
            sql_query = f"""
            create table {self.table_name} (
                image_name nvarchar(40),
                date_time DATETIME(3),
                distances decimal(19,4),
                distance_updated decimal(19,4),
                avg_distance decimal(19,4),
                distance_limit float
            )
            
            """
            self.dbConnection.execute(sql_query)
        
        else: pass


    def _table_existence(self):

        # cursor = self.dbConnection.execute()
        sql_query = f"""
                SELECT COUNT(*)
                FROM information_schema.tables 
                WHERE table_schema = 'face_to_monitor_distance'
                AND table_name=  '{self.table_name}'
        """

        cursor = self.dbConnection.execute(sql_query)

        row = cursor.fetchone()

        if  row[0] == 1:
            return True

        else: return False

    def insert_table(self, input: list) -> None:
        image_name, date_time, distances, distance_updated, avg_distance, distance_limit = input
        sql_query = f"""
            insert into {self.table_name}(image_name, date_time, distances, distance_updated, avg_distance, distance_limit)
            values('{image_name}','{date_time}',{round(distances,4)},{round(distance_updated,4)},{round(avg_distance,4)},{distance_limit})
        """

        self.dbConnection.execute(sql_query)