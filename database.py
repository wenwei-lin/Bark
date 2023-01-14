import sqlite3

class DatabaseManager:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
    
    def __del__(self):
        """
        Cleanup database connection when deleting object
        """
        self.connection.close()
    
    def _execute(self, statement, values=None):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(statement, values or [])
            return cursor
    
    def create_table(self, table_name: str, columns: dict):
        """
        Generalize create table action
        """
        # Turn columns dict to list of (column_name, column_type) for functional programming
        columns_with_types = [
            f"{column_name} {column_type}"
            for column_name, column_type in columns.items()
        ]

        statement = f"""
            CREATE TABLE IF NOT EXISTS {table_name}(
                {', '.join(columns_with_types)}
            );
        """
        self._execute(statement)
    
    def add(self, table_name, data: dict):
        placeholders = ', '.join("?" * len(data))
        column_names = data.keys()
        column_values = data.values()

        self._execute(
            f"""
            INSERT INTO {table_name}({", ".join(column_names)})
            VALUES ({placeholders});
            """,
            column_values
        )
    
    def delete(self, table_name, criterial:dict):
        placeholders = [f"{column_name} = ?" for column_name in criterial.keys()]
        self._execute(
            f"""
            DELETE FROM {table_name}
            WHERE {' AND '.join(placeholders)}
            """,
            criterial.values()
        )
    
    def select(self, table_name, criterial=None, order_by=None):
        criterial = criterial or {}
        query = f"SELECT * FROM {table_name}"

        if criterial:
            placeholders = [f"{column_name} = ?" for column_name in criterial.keys()]
            query += f" WHERE {' AND '.join(placeholders)}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        return self._execute(query, criterial.values())
