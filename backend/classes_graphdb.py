class Jdbc:
    """
        Class definition for "JDBC" database type.
        
        Paramaters:
            host: string 
            service_name: string 
            priority: string
    """
    def __init__(self, host, service_name, priority):
        self.host= host
        self.service_name = service_name
        self.priority = priority
    def __repr__(self):
        return f"{self.host},{self.service_name},{self.priority}"

class Nosql:
    """
        Class definition for "NoSQL" database type.
        
        Paramaters:
            host: string 
    """
    def __init__(self, host):
        self.host =  host

    def __repr__(self):
        return f"{self.host}"
    
class Rest:
    """
        Class definition for "REST".
        
        Paramaters:
            service: string 
            port: string 
    """
    def __init__(self, service, port):
        self.service = service
        self.port =  port
    def __repr__(self):
        return f"{self.service},{self.port}"


class Grpc:
    """
        Class definition for "GRPC".
        
        Paramaters:
            service: string 
            port: string 
    """
    def __init__(self, service, port):
        self.service = service
        self.port =  port
    def __repr__(self):
        return f"{self.service},{self.port}"


class Online:
    """
        Class definition of "Online" type which represents the dependencies of microservices.
        Online type consists the lists of the dependancy types through grpc or rest. 
        
        Parameters:
            grpc_ls: list of GRPC objects 
            rest_ls: list of REST objects  
    """
    def __init__(self, grpc_ls, rest_ls):
        #two list
        self.grpc_nodes = grpc_ls
        self.rest_nodes = rest_ls

    def __repr__(self):
        sl = []
        for g in self.grpc_nodes:
            sl.append(g)
        for r in self.rest_nodes:
            sl.append(r)
        return(str(sl))
        
class Data:
    """
        Class definiton of "Data" type.
        Data type consists of the information of the where the data resides in.
        
        Parameters:
            jdbc_node: list of JDBC objects
            nosql_node: list of NoSQL objects
    """
    def __init__(self, jdbc_node, nosql_node):
        #two list

        self.jdbc_node = jdbc_node
        self.nosql_node =  nosql_node

    def __repr__(self):
        sl = []
        for g in self.jdbc_node:
            sl.append(g)
            
        sl.append(self.nosql_node.host)
        return(str(sl))
    

class Microservice:
    """
        Class definition of Microservice.
        Microservice instances encapsulate all the descriptive information
        which depicts the characteristics of the microservice, database based relations
        and the dependencies of the microservice.
        
        Parameters:
            name: str 
                name of the microservice 
            version: str
                version of the microservice
            namespace: str
                namespace of the microservice
            org_code: str
                organisational code of the microservice 
            online_node: [Online]
                dependency information of the microservice is stored in Online obj
            data_node: [Data]
                desribtion of the database information of the microservice that which 
                data is used in which database type (NoSQL or JDBC)  
    """     
    def __init__(self, name, version, namespace, org_code, online_node, data_node):
        self.name =  name
        self.version =  version
        self.namespace =  namespace
        self.org_code =  org_code
        self.online_node =  self.online_node_creator(online_node) #obj
        self.data_node =  self.data_node_creator(data_node) # obj

    def online_node_creator(self,o):
        """
            
            Creates and Returns Online object instance.
            Based on the relations that is present in the micoroservice,
            GRPC and REST instances are created accordingly and they are grouped in seperate lists.
            With the list of GRPC and REST, Online obj is created. 
            
            Args: 
                o: dict
                    dictionary which conatins the "grapc", and "rest" keys 
            Returns:
                online_node_inst: Online(obj)
                    online node instance  
        """
        grpc_node_list = []
        rest_node_list = []

        if "grpc" in o.keys(): # if "grpc" key is present in the dict"
            grpc_class = o["grpc"]
            for dict in grpc_class['clients']:
                #create a GRPC instance
                grpc_node = Grpc(dict['service'], dict['port'])
                grpc_node_list.append(grpc_node) # append the obj to list 

        if "rest" in o.keys(): # if "rest" key is present in the dict"
            rest_class = o['rest']
            for dict in rest_class['clients']:
                #create a REST instance
                rest_node = Rest(dict['service'], dict['port'])
                rest_node_list.append(rest_node) # append the obj to list 

        online_node_inst = Online(grpc_node_list, rest_node_list) # Online instance is created 

        return online_node_inst

    def data_node_creator(self,o):
        """
            Creates and Returns a Data objects instance.
            
            Based on the database information that the microservice contains,
            JDBC and NoSQL objects are created and stored in a list, which the two list will be
            in order to create the Data instance.
            
            Args:
                o: dict
                    dictionary which conatins the "grapc", and "rest" keys 
            Returns: 
                data_node_inst: Data(obj)
                    Data node instance
        """
        jdbc_node_list = []
        nosql_node_list = []
        if "jdbc" in o.keys():
            jdbc_class = o['jdbc']
            jdbc_data_source = jdbc_class['datasource']
            if "primary" in jdbc_data_source.keys():
                jdbc_attr_class_source = jdbc_data_source['primary']
                jdbc_attr_class = jdbc_attr_class_source['url']
                jdbc_node = Jdbc(
                    jdbc_attr_class['host'], jdbc_attr_class['service_name'], "primary")
                jdbc_node_list.append(jdbc_node)
            if "secondary" in jdbc_data_source.keys():
                jdbc_attr_class_source = jdbc_data_source['secondary']
                jdbc_attr_class = jdbc_attr_class_source['url']
                jdbc_node = Jdbc(
                    jdbc_attr_class['host'], jdbc_attr_class['service_name'], "secondary")
                jdbc_node_list.append(jdbc_node)
        if "nosql" in o.keys():
            nosql_class = o['nosql']
            nosql_data_source = nosql_class['datasource']
            nosql_node = Nosql(nosql_data_source['url'])
            nosql_node_list.append(nosql_node)

        data_node_inst = Data(jdbc_node_list, nosql_node_list)

        return data_node_inst

    def __repr__(self):
            
        return f"{self.name},{self.version},{self.namespace},{self.org_code},{self.online_node}, {self.data_node}"