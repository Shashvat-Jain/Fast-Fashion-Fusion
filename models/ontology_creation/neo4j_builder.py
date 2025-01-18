import json
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import load_ontology as lo
load_dotenv()


class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

def merge_create_nodes(conn, label, data):
    # Adds nodes with a dynamic label to the Neo4j graph.
    query = f'''
            UNWIND $rows AS row
            MERGE (n:{label} {{name: row.name}})
            RETURN count(*) as total
            '''
    res = conn.query(query, parameters={'rows': data})
    print(res)
    return res

def create_nodes(conn, label, data):
    query = f'''
            UNWIND $rows AS row
            CREATE (n:{label} {{name: row.name}})
            RETURN count(*) as total
            '''
    res = conn.query(query, parameters={'rows': data})
    print(res)
    return res

def merge_create_relationship_with_one_node(conn, r_from, r_to, from_name, to_name):
    query = f'''
    MATCH (p:{r_to} {{name: $to_name}})
    MERGE (a:{r_from} {{name: $from_name}})
    MERGE (a)-[:BELONGS_TO]->(p)
    RETURN a, p
    '''
    res = conn.query(query, parameters={"from_name": from_name, "to_name": to_name})
    print(res)
    return res

def create_relationship_with_one_node(conn, r_from, r_to, from_name, to_name):
    query = f'''
    MATCH (p:{r_to} {{name: $to_name}})
    CREATE (a:{r_from} {{name: $from_name}})
    CREATE (a)-[:BELONGS_TO]->(p)
    RETURN a, p
    '''
    res = conn.query(query, parameters={"from_name": from_name, "to_name": to_name})
    print(res)
    return res

def merge_create_relationship(conn, r_from, r_to, from_name, to_name):
    query = f'''
    MATCH (a:{r_from} {{name: $from_name}}), (p:{r_to} {{name: $to_name}})
    MERGE (a)-[:BELONGS_TO]->(p)
    RETURN a, p
    '''
    res = conn.query(query, parameters={"from_name": from_name, "to_name": to_name})
    print(res)
    return res



def create_nodes_main():
    ontology_lists = lo.create_ontology_lists(lo.read_json("ontology.json"))
    conn = Neo4jConnection(uri="neo4j+s://9af3a233.databases.neo4j.io", user="neo4j", pwd="qvAvMXmTz4QXr3Q64ZVy9ZFYqBMWKTBBV2ejkXGhn5I")

    print("\n\n ontology: ", ontology_lists)

    conn.query('CREATE CONSTRAINT superclass IF NOT EXISTS FOR (p:superclass) REQUIRE p.name IS UNIQUE')
    conn.query('CREATE CONSTRAINT subclass IF NOT EXISTS FOR (a:subclass) REQUIRE a.name IS UNIQUE')
    conn.query('CREATE CONSTRAINT subsubclass IF NOT EXISTS FOR (c:subsubclass) REQUIRE c.name IS UNIQUE')
    conn.query('CREATE CONSTRAINT category IF NOT EXISTS FOR (c:category) REQUIRE c.name IS UNIQUE')
    conn.query('CREATE CONSTRAINT product IF NOT EXISTS FOR (n:product) REQUIRE n.id IS UNIQUE')

    all_superclasses = [{"name": name} for name in ontology_lists["superclasses"]]
    all_subclasses = [{"name": name} for name in ontology_lists["subclasses"]]
    all_subsubclasses = [{"name": name} for name in ontology_lists["subsubclasses"]]
    all_categories = [{"name": name} for name in ontology_lists["categories"]]

    merge_create_nodes(conn, "superclass", all_superclasses)
    merge_create_nodes(conn, "subclass", all_subclasses)
    merge_create_nodes(conn, "subsubclass", all_subsubclasses)
    merge_create_nodes(conn, "category", all_categories)

    return
    
def create_releationships_main():
    data = lo.read_json("ontology.json")
    conn = Neo4jConnection(uri=os.getenv('NEO4J_URI'), user=os.getenv('neo4j'), pwd=os.getenv('NEO4J_PASSWORD'))
    for superclass in data.get("superclass", []):
        print(f"Superclass: {superclass['name']}")
        merge_create_nodes(conn, "superclass", [{"name": superclass['name']}])
        for subclass in superclass.get("subclass", []):
            print(f"  Subclass: {subclass['name']}")
            create_relationship_with_one_node(conn, "subclass", "superclass", subclass['name'], superclass['name'])
            for subsubclass in subclass.get("subsubclass", []):
                print(f"    Subsubclass: {subsubclass['name']}")
                create_relationship_with_one_node(conn, "subsubclass", "subclass", subsubclass['name'], subclass['name'])
                for category in subsubclass.get("category", []):
                    print(f"      Category: {category['name']}")
                    create_relationship_with_one_node(conn, "category", "subsubclass", category['name'], subsubclass['name'])
                    for product in category.get("product", []):
                        print(f"        Product: {product['name']}")
                        create_relationship_with_one_node(conn, "product", "category", product['name'], category['name'])
    return

if __name__ == '__main__':
    # create_nodes_main()
    create_releationships_main()