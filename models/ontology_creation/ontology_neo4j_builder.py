import json
from neo4j import GraphDatabase
import os


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__pwd)
            )
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
            session = (
                self.__driver.session(database=db)
                if db is not None
                else self.__driver.session()
            )
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


def merge_create_nodes(conn, label, data):
    query = f"""
        UNWIND $rows AS row
        MERGE (n:{label} {{name: row.name}})
        RETURN count(*) as total
    """
    res = conn.query(query, parameters={"rows": data})
    print(f"Created {label} nodes:", res)


def create_relationship_with_one_node(conn, r_from, r_to, from_name, to_name):
    query = f"""
        MATCH (p:{r_to} {{name: $to_name}})
        MERGE (a:{r_from} {{name: $from_name}})
        MERGE (a)-[:BELONGS_TO]->(p)
        RETURN a, p
    """
    res = conn.query(query, parameters={"from_name": from_name, "to_name": to_name})
    print(f"Created relationship: {from_name} -> {to_name}")


def create_relationships_from_json(data, conn):
    for superclass_name, superclass_data in data.items():
        merge_create_nodes(conn, "superclass", [{"name": superclass_name}])

        if "classes" in superclass_data:
            for class_name in superclass_data["classes"]:
                create_relationship_with_one_node(
                    conn, "class", "superclass", class_name, superclass_name
                )

                if class_name in superclass_data:
                    class_data = superclass_data[class_name]

                    if "types" in class_data:
                        for subclass_name in class_data["types"]:
                            create_relationship_with_one_node(
                                conn, "subclass", "class", subclass_name, class_name
                            )

                            if subclass_name in class_data:
                                subclass_data = class_data[subclass_name]

                                if "variants" in subclass_data:
                                    for variant_name in subclass_data["variants"]:
                                        create_relationship_with_one_node(
                                            conn,
                                            "variant",
                                            "subclass",
                                            variant_name,
                                            subclass_name,
                                        )

                                if "styles" in subclass_data:
                                    for style_name in subclass_data["styles"]:
                                        create_relationship_with_one_node(
                                            conn,
                                            "style",
                                            "subclass",
                                            style_name,
                                            subclass_name,
                                        )


if __name__ == "__main__":
    json_data = {}
    with open("VERIFIED_ONTOLOGY.json", "r") as file:
        json_data = json.load(file)
    # print(json_data)
    conn = Neo4jConnection(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USERNAME"),
        pwd=os.getenv("NEO4J_PASSWORD"),
    )
    create_relationships_from_json(json_data, conn)

    conn.close()
