import psycopg2


class PostgresORM:
    def __init__(self, dbname, user, password, host='localhost', port=5431):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor()

    def create_table(self):
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS api (
            id SERIAL PRIMARY KEY,
            featureOne float4 NOT NULL,
            featureTwo float4 NOT NULL,
            featureStart int4 NOT NULL
        );
        '''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def delete_by_id(self, id):
        pass

    def add(self, feature_one, feature_two, feature_start):
        insert_query = '''
        INSERT INTO api (featureone, featuretwo, featurestart) 
        VALUES (%s, %s, %s);
        '''
        data = [feature_one, feature_two, feature_start]
        try:
            self.cursor.execute(insert_query, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(type(e), "error occurred")

    def get_by_id(self, ids):
        select_query = '''
        SELECT * FROM api
        WHERE id = %s
        '''
        data = [id]
        self.cursor.execute(select_query, data)

    def get_all(self):
        select_query = '''
                SELECT * FROM api
                WHERE id = %s
                '''
        data = [id]
        self.cursor.execute(select_query, data)
