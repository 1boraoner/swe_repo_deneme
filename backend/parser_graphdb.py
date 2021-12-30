from github import Github
from pprint import pprint
import xml.etree.ElementTree as ET
import yaml


def read_pom(pom_point):
    """
    
    Parses the input POM.xml file which contains the microservice's characteristic informations. 
    
    Args:
        pom_point: ContentFile()
            pom_point is the content file which is a type defined in ElementTree module.
            It contains the pom file as its attributes.
    Returns:
        root: ElementTree(obj)
            the root tag of the parsed .xml file. the root is the pointed of the document and 
            from root all the tags can be reached. 

    """
    pom_file = pom_point.decoded_content.decode() # pom file content is decoded

    # original pom file has some links on the head  tag which effect the output of the parsing
    # the links will be erased. 
    pom_file.split('\n')
    # the parsed string is decomposed to lines
    cleaned = [line for i, line in enumerate(
        pom_file.split('\n')) if not (i > 0 and i < 4)]
    # the cleaned head tag is inserted
    cleaned.insert(1, "<project>")
    d = ('\n').join(cleaned)

    # the xml file is parsed from stirng
    root = ET.fromstring(d)
    return root


def read_yaml(yaml_file):
    """
    Parses the yaml file which contains the information of dependecies and database informations
    of the microservice
    
    Args:
        yaml_file: ContentFile()
            the content file that is extracted from the github repository
    Returns:
        yaml_dict: dict
            parsed yaml file as a dictonary. The keys of the dictionary corresponds to the 
            tags in the yaml file. 
    """
    yaml_str = yaml_file.decoded_content.decode()
    yaml_dict = yaml.load(yaml_str, Loader=yaml.FullLoader)
    return yaml_dict


def traverse_svc(repo, path, svc):

    """
    Traverses the github repository inputted and in each iteration extracts the pom.xml and .yaml 
    files present in the microservice folders in the reporsitory.
    
    Args:
        repo: Repository()
            repo is the indicator for the reading the folders in the repo. From the repo all 
            svc folder can be reached.
        path: string
            path of the directory relative to the github repository.
        svc: ContentFile()
            svc contains the files and their content which are under the folder in the svc-x folder in the
            github repository. each svc-x folder corresponds to a Microservice.
    Returns:
        content: Element
            content is the parsed pom.xml file. It is Element type which is defined in the ElementTree module
        yf: dict
            yf is the parsed yaml file
        
    """
    
    svc_docs = repo.get_contents(svc) # the microservice contents and files
    
    # iterate over the documents under the svc folder
    for doc in svc_docs:
        
        # the _app folders under the svc's corresponds to a path to yaml files of the microservices
        if "app" in doc.path:

            # app yaml file
            yaml_path = "src/main/resources/application.yml"
            yaml_f = repo.get_contents(doc.path + "/" + yaml_path)
            yf = read_yaml(yaml_f) # parse the information 
        
        # from the pom.xml file other information about microservices can be extracted.
        elif "pom.xml" in doc.path:
            pom = repo.get_contents(doc.path)
            content = read_pom(pom) # parse pom.xml file
        else:
            # other folders which does not have a signficant use in the context of our project
            pass
    return content, yf
