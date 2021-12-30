from neo4j import GraphDatabase
from object_creator import *
import time
from collections import defaultdict
import json


class Connector:
    """
        Class definiton of Connector class objects. Connector defines the graph database
        connection and the contains all the CRUD operations which can be used accorindly

        Parameters:

        uri: str
            an identifier for the database accessing operations
        user: str
            user information in order to access the database
        password: str
            password information in order to access the database

    """

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
            closes the connection to the database
        """
        self.driver.close()

    def create_db(self, obj):
        """
            creates the database instances in the existing graph which are located in "data_node" object.
        """

        with self.driver.session() as session:
            obj_type = "Microservice"
            for jdbc_node in obj.__dict__['data_node'].jdbc_node:
                host_attr = jdbc_node.__dict__['host']
                return_msg = session.write_transaction(
                    self._create_node_helper, 'host', host_attr, 'Data')
                return_msg = session.write_transaction(
                    self._create_relation_helper,  "Data", obj_type, 'host', host_attr, 'name', obj.name, 'USED_IN')
                return_msg = session.write_transaction(
                    self._set_node_helper, "Data", "host", host_attr, "type", "JDBC")
                for key_jdbc in jdbc_node.__dict__.keys():
                    attr_jbdc = jdbc_node.__dict__[key_jdbc]
                    return_msg = session.write_transaction(
                        self._set_node_helper, "Data", "host", host_attr, key_jdbc, attr_jbdc)
                    pass
            for nosql_node in obj.__dict__['data_node'].nosql_node:
                host_attr = nosql_node.__dict__['host']
                return_msg = session.write_transaction(
                    self._create_node_helper, 'host', host_attr, 'Data')
                return_msg = session.write_transaction(
                    self._create_relation_helper, "Data", obj_type, 'host', host_attr, 'name', obj.name, 'USED_IN')
                return_msg = session.write_transaction(
                    self._set_node_helper, "Data", "host", host_attr, "type", "NOSQL")

    def create_rel(self, obj):
        """
            the function which creates the relations of the given objects. Accesses the classes inside the object
            and uses the related classes which are located at "online_nodes".
        """
        with self.driver.session() as session:
            obj_type = "Microservice"
            attr = obj.__dict__['online_node']
            for grpc_node in attr.grpc_nodes:
                for key_grpc in grpc_node.__dict__.keys():
                    if key_grpc == 'service':
                        return_msg = session.write_transaction(
                            self._create_relation_helper,  obj_type, obj_type, 'name', obj.name, 'name', grpc_node.__dict__[key_grpc], 'GRPC')
                    elif key_grpc == 'port':
                        return_msg = session.write_transaction(
                            self._set_rel_helper, obj_type, obj_type, 'name', obj.name, 'name', grpc_node.__dict__['service'], 'GRPC', 'port', grpc_node.__dict__[key_grpc])
            for rest_node in attr.rest_nodes:
                for key_rest in rest_node.__dict__.keys():
                    if key_rest == 'service':
                        return_msg = session.write_transaction(
                            self._create_relation_helper, obj_type, obj_type, 'name', obj.name, 'name', rest_node.__dict__[key_rest], 'REST')
                    elif key_rest == 'port':
                        return_msg = session.write_transaction(
                            self._set_rel_helper, obj_type, obj_type, 'name', obj.name, 'name', rest_node.__dict__['service'], 'REST', 'port', rest_node.__dict__[key_rest])

    def set_node(self, obj):
        """
            the function which sets the attributes of the given objects
        """

        with self.driver.session() as session:
            obj_type = "Microservice"
            for key in obj.__dict__.keys():
                attr = obj.__dict__[key]
                if (type(attr) != Online) and (type(attr) != Data):
                    session.write_transaction(
                        self._set_node_helper, obj_type, 'name', obj.name, key, attr)

    def create_node(self, _match_key, _match_attr, _match_type):
        """
            the function which creates the object with given key, attribute, and type.
        """

        with self.driver.session() as session:
            session.write_transaction(
                self._create_node_helper, _match_key, _match_attr, _match_type)

    def truncate_db(self):
        """
            clears the database.
        """

        with self.driver.session() as session:
            session.write_transaction(self._truncate_db)

    def read_database(self):
        """
            reads the database and returns the graph objects to be used to represent graph.
        """

        with self.driver.session() as session:
            query = "MATCH p = ((a)-[r]->(b)) RETURN *"
            results = session.run(query)
            # pprint(results.data())
            graph = results.graph()
            return graph

    @staticmethod
    def _set_rel_helper(tx, _type_first, _type_second, _match_type_1, _match_attr_1, _match_type_2, _match_attr_2, _relation_type, _rel_attr_key, _rel_attr_val):
        """
            runs the cypher query which sets the attributes of relations between given nodes.

            Args:

                _type_first: str
                    the type used to match the first node.
                _type_second: str
                    the type used to match the second node.
                _match_type_1: str
                    the match type will be used to match the first node.
                _match_attr_1: str
                    the first attribute of the key which will be used to match the first node.
                _match_type_2: str
                    the first match type will be used to match the second node.
                _match_attr_2: str
                    the attribute of the key which will be used to match the second node.
                _relation_type: str
                    relation type used to match the relation between node-1 and node-2
                _rel_attr_key: str
                    attribute key which will be created in the relation between node-1 and node-2
                _rel_attr_val: str
                    attribute value which will be created in the relation between node-1 and node-2
        """
        result = tx.run("MATCH "
                        "(a:"+_type_first+"), "
                        "(b:"+_type_second+") "
                        "WHERE a."+_match_type_1+" = $match_attr_1 AND b." +
                        _match_type_2+" = $match_attr_2 "
                        "MERGE (a)-[r:"+_relation_type+"]->(b) "
                        "SET r."+_rel_attr_key+" = $rel_attr_val", match_attr_1=_match_attr_1, match_attr_2=_match_attr_2, rel_attr_val=_rel_attr_val)

    @staticmethod
    def _create_relation_helper(tx, _type_first, _type_second, _match_key_1, _match_attr_1, _match_key_2, _match_attr_2, _relation_type):
        """
            runs the cypher query which creates relations between nodes.

            Args:
                _type_first: str
                    the first type used to match the node.
                _match_attr_1: str
                    the first attribute of the key which will be used to match the first node.
                _match_key_1: str
                    the match key will be used to match the first node.
                _type_second: str
                    the second type used to match the node.
                _match_attr_2: str
                    the attribute of the key which will be used to match the second node.
                _match_key_2: str
                    the first match key will be used to match the second node.
                _relation_type: str
                    relation type which will be created between node-1 and node-2
        """
        result = tx.run("MATCH "
                        "(a:"+_type_first+"), "
                        "(b:"+_type_second+") "
                        "WHERE a."+_match_key_1+" = $match_attr_1 AND b."+_match_key_2+" = $match_attr_2 "
                        "CREATE (a)-[r:"+_relation_type+"]->(b) "
                        "RETURN type(r) + ', from node ' + id(a)", match_attr_1=_match_attr_1, match_attr_2=_match_attr_2)

    @staticmethod
    def _set_node_helper(tx, _match_type, _match_key, _match_attr, _key, _val):
        """
            runs the cypher query which sets the attributes of the given node type which matches the
            key and attribute values.

            Args:

                _match_type: str
                    the match type which will be created.
                _match_key: str
                    the key which will be created.
                _match_attr: str
                    the attribute of the key which will be created.
                _key: str
                    the key which will be used to set the attributes.
                _val:str
                    the value which will be used to set the attributes.
        """
        result = tx.run("MATCH "
                        "(a:"+_match_type+") "
                        "WHERE a."+_match_key+" = $match_attr "
                        "SET a."+_key+" = $val ", match_attr=_match_attr, val=_val)

    @staticmethod
    def _create_node_helper(tx, _match_key, _match_attr, _match_type):
        """
            runs the cypher query which creates the node with the given type.

            Args:

                _match_key: str
                    the key which will be created.
                _match_attr: str
                    the attribute of the key which will be created.
                _match_type: str
                    the match type which will be created.

        """
        result = tx.run("MERGE (a { "+_match_key+": $match_attr }) "
                        "SET a:"+_match_type+" "
                        "RETURN a", match_attr=_match_attr)
        return result.single()[0]

    @staticmethod
    def _truncate_db(tx):
        """
            Truncates the database by deleting every node that is created in the database.
        """

        result = tx.run("MATCH (n) "
                        "DETACH DELETE n ")


def format_results(result_graph):
    node_list = []
    # for node in result_graph.nodes:
    #     node_di = defaultdict()
    #     if "name" not in node._properties.keys():
    #         node_di["id"] = node._properties["host"]
    #     else:
    #         node_di["id"] = node._properties["name"]

    #     for l in node.labels:
    #         node_di["labels"] = l
    #     node_di["properties"] = {}
    #     for k, i in node.items():
    #         node_di["properties"][k] = i
    #     node_list.append(node_di)

    for node in result_graph.nodes:
        node_di = defaultdict()
        node_di["id"] = node.id
        for l in node.labels:
            node_di["labels"] = l
        node_di["properties"] = {}
        for k, i in node.items():
            node_di["properties"][k] = i
        node_list.append(node_di)

    # READING AND PARSING DATABASE RELATIONS
    rel_list = []
    for rel in result_graph.relationships:
        r = defaultdict()
        r["id"] = rel.id
        for k, i in rel.start_node.items():
            if "name" not in rel.start_node.keys():
                if k == "host":
                    r["start_node"] = i

            if k == "name":
                r["start_node"] = i

        for k, i in rel.end_node.items():
            if k == "name":
                r["end_node"] = i

        r["type"] = rel.type
        r["properties"] = rel._properties
        rel_list.append(r)

    formatted_results = {}
    formatted_results["Nodes"] = node_list
    formatted_results["Relationships"] = rel_list
    return formatted_results


def fetch_db_data():
    start = time.time()

    uri = "neo4j+s://1f712780.databases.neo4j.io"
    username = "neo4j"
    password = "9YhVLNStKFTbuoHY3bRADqkU9bobATh1kXp2mZr52uo"

    connector = Connector(uri, username, password)

    # If set True -> truncate all data in db and re-create the database
    START_OVER_AGAIN = False
    if START_OVER_AGAIN == True:
        connector.truncate_db()
        mic_svc_list = main_object()
        for mic_svc in mic_svc_list:
            connector.create_node('name', mic_svc.name, 'Microservice')
            connector.set_node(mic_svc)
        for mic_svc in mic_svc_list:
            connector.create_rel(mic_svc)
            connector.create_db(mic_svc)

    result_graph = connector.read_database()
    # READING AND PARSING DATABASE NODES
    formatted_results = format_results(result_graph)

    DEBUG = False
    if DEBUG == True:

        #     # JSONIFY NODES AND RELATIONS
        #     with open("graph_results.txt", "w") as f:
        #         for node in node_list:
        #             f.write(json.dumps(node))
        #             f.write("\n")

        #     with open("graph_relations.txt", "w") as f:
        #         for rel in rel_list:
        #             f.write(json.dumps(rel))
        #             f.write("\n")

        with open("response.txt", "w") as f:
            f.write(json.dumps(formatted_results))

    end = time.time()
    print("The execution is completed in "+str(end - start)+" seconds")
    connector.close()

    return formatted_results


# if __name__ == '__main__':
#     fetch_db_data()
