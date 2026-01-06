from abc import ABC, abstractmethod
import sqlite3
import json
import pyodbc
import logging


class database(ABC):
    @abstractmethod
    def insert(self,cleaned_chunks, embeddings_np, file_name):
        pass
    def delete(self):
        pass
    def retrieval(self):
        pass

class sqlite(database):
    def insert(self, cleaned_chunks, embeddings_np, file_name):
        connection = sqlite3.connect("db.db")
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunk_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk TEXT NOT NULL,
            embedding INTEGER,
            name TEXT NOT NULL
        )
        """)
        connection.commit()
        print('Table ensured to exist.')

        embeddings_json = [json.dumps(item.tolist()) for item in embeddings_np]
        print('Embeddings converted to JSON successfully.')
        chunk_info_list = [(cleaned_chunks[i], embeddings_json[i], file_name) for i in range(len(cleaned_chunks))]
        print('Chunk info list prepared.')

        cursor.executemany("""
        INSERT INTO chunk_info (chunk, embedding, name)
        VALUES (?, ?, ?)
        """, chunk_info_list)
        connection.commit()
        connection.close()
        print('sqlite database updated successfully.')

        return f"sqlite database updated successfully with file: {file_name}"


    def delete(self, file_name):

        connection = sqlite3.connect("db.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM chunk_info")
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from sqlite database.")

        file_name_list = []
        for row in rows:
            file_name_list.append(row[3])
        print(len(file_name_list))
        print(file_name)

        if file_name not in file_name_list:
            response = f"No entries found with file: {file_name} in sqlite database."
            print(response)
            return response
        else:
            cursor.execute("""
            DELETE FROM chunk_info
            WHERE name = ?
            """, (file_name,))
            response = f"Deleted entries with file: {file_name} from sqlite database."
            connection.commit()
        connection.close()
        print(response)

        return response


    def retrieval(self):
        connection = sqlite3.connect("db.db")
        print('Connecting to sqlite database...')
        cursor = connection.cursor()
        print('sqlite database connected successfully.')

        cursor.execute("SELECT * FROM chunk_info")
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from database.")

        cleaned_chunks = []
        file_name_list = []
        embeddings_np = []
        for row in rows:
            cleaned_chunk, embeddings_json, file_name=row[1], row[2], row[3]
            cleaned_chunks.append(cleaned_chunk)
            file_name_list.append(file_name)
            embeddings = json.loads(embeddings_json)
            embeddings_np.append(embeddings)
        print(len(embeddings))
        connection.close()
        print('Data loaded from sqlite database successfully.')

        return cleaned_chunks, embeddings_np, file_name_list


class sqlserver(database):
    def insert(self, cleaned_chunks, embeddings_np, file_name):
        connection_string = "Driver={ODBC Driver 17 for SQL Server};Server=tcp:xxx.database.windows.net,1433;Database=xxx;Authentication=ActiveDirectoryMsi;Connection Timeout=240;Encrypt=yes;TrustServerCertificate=no"

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print('SQL Server database connected successfully.')

        table_name = 'chunk_info'
        schema_name = 'dbo'

        create_table = f"""
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[{schema_name}].[{table_name}]') AND type in (N'U'))
        BEGIN
            CREATE TABLE [{schema_name}].[{table_name}] (
                id INT PRIMARY KEY IDENTITY(1,1),
                chunk NVARCHAR(MAX) NOT NULL,
                embedding NVARCHAR(MAX) NOT NULL,
                file_name NVARCHAR(MAX) NOT NULL,
            );
            PRINT 'Table "{schema_name}.{table_name}" created successfully.';
        END
        ELSE
        BEGIN
            PRINT 'Table "{schema_name}.{table_name}" already exists. Skipping creation.';
        END
        """
        print('Ensuring table exists...')

        cursor.execute(create_table)
        conn.commit()

        insert_query = f"""
        INSERT INTO [{schema_name}].[{table_name}] (chunk, embedding, file_name)
        VALUES (?, ?, ?);
        """
        print('Preparing to insert data into SQL Server database...')

        embeddings_json = [json.dumps(item.tolist()) for item in embeddings_np]
        print('Embeddings converted to JSON successfully.')
        chunk_info_list = [(cleaned_chunks[i], embeddings_json[i], file_name) for i in range(len(cleaned_chunks))]
        print('Chunk info list prepared for insertion.')

        cursor.executemany(insert_query, chunk_info_list)
        conn.commit()
        print('Data inserted into SQL Server database successfully.')

        cursor.close()
        conn.close()
        return f"SQL server database updated successfully with file: {file_name}"


    def delete(self, file_name):
        connection_string = "Driver={ODBC Driver 17 for SQL Server};Server=tcp:xxx.database.windows.net,1433;Database=xxx;Authentication=ActiveDirectoryMsi;Connection Timeout=240;Encrypt=yes;TrustServerCertificate=no"
        print('Connecting to SQL Server database...')
        conn = pyodbc.connect(connection_string)
        print('SQL Server database connected successfully.')
        cursor = conn.cursor()
        print('Connecting to SQL Server database for retrieval...')

        cursor.execute("SELECT * FROM chunk_info")
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from SQL server database.")

        file_name_list = []
        for row in rows:
            file_name_list.append(row[3])
        print(len(file_name_list))
        print(file_name)

        if file_name not in file_name_list:
            response = f"No entries found with file: {file_name} in SQL server database."
            print(response)
            return response
        else:
            cursor.execute("""
            DELETE FROM chunk_info
            WHERE file_name = ?
            """, (file_name,))
            response = f"Deleted entries with file: {file_name} from SQL server database."
            conn.commit()
        conn.close()
        print(response)

        return response

    def retrieval(self):
        connection_string = "Driver={ODBC Driver 17 for SQL Server};Server=tcp:xxx.database.windows.net,1433;Database=xxx;Authentication=ActiveDirectoryMsi;Connection Timeout=240;Encrypt=yes;TrustServerCertificate=no"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print('Connecting to SQL Server database for retrieval...')

        cursor.execute("SELECT * FROM chunk_info")
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from SQL server database.")
        cleaned_chunks = []
        file_name_list = []
        embeddings_np = []
        for row in rows:
            cleaned_chunk, embeddings_json, file_name=row[1], row[2], row[3]
            cleaned_chunks.append(cleaned_chunk)
            file_name_list.append(file_name)
            embeddings = json.loads(embeddings_json)
            embeddings_np.append(embeddings)
        print(len(embeddings))
        conn.close()
        print('Data loaded from SQL server database successfully.')

        return cleaned_chunks, embeddings_np, file_name_list
