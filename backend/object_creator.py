from classes_graphdb import *
from parser_graphdb import *

def github_repo_definer():
    """
    
    With the use of Gİthub module and the user token the repository where the 
    microservice data is placed is reached.
    
    Returns:

        main_path: str
            the main path of the github url    

        repo: Github.Repository.Repository(obj)
            repo is the identifier of the repository which is a github repository 
            object. From the repo all the content underit can be reaced.
        
        
    """
    
    token = "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"
    g = Github(token)
    main_path = "susantez/sdc-input-data"
    repo = g.get_repo(main_path)

    return main_path, repo

def object_creator(pom_content, yaml_file):
    """

        Creates the microservice instance from the parsed yaml and pom.xml files and returns the created object. 
    
    Args:
        pom_content: Element(obj)
            parsed pom.xml file which will be used in order to get the microservice informaiton.
        yaml_file: dict
            parsed yaml file content, which will be used in order to create the microservice instance

    Returns:
        created_mic_svc: Microservice(obj)
            microservice instance which ecapsulates the information of the microservice 
            that is parsed from the repo folders.
    
    """
    
    
    #extracting relevant informations from the parsed documents
    
    app_class = yaml_file['app'] # app key is the root of the dictionary
    
    namespace = app_class['namespace']  # namespace information
    org_code = app_class['org-code']    # organization information
    online_class = app_class['online']  # online information
    data_class = app_class['data']      # data information 
    artifact_id = pom_content.find('artifactId').text   # artifact_id of the microservice 
    version = pom_content.find('version').text          # version of the microservice
    
    # microservice instance created
    created_mic_svc = Microservice(
        artifact_id, version, namespace, org_code, online_class, data_class)

    return created_mic_svc


def main_object():
    
    """

    extract all microservices that is in the github repository by traversing the svc-x folders.
    creates a list of microservices and returns it.
    
    Returns:
        microservice_list: list
            contains the microservice instances that corresponds to each svc folders in the github repository.
                
    """
    
    main_path, repo = github_repo_definer() # get auth from github and repo
    microservice_list = [] # microservice list which contains the all microservices

    for pross in repo.get_contents(""):
        if "md" in pross.path: # READ.md file of the repo is jumped over
            continue
        
        # pom file and yaml file content of the microservice
        returned_pom_content, returned_yaml = traverse_svc(
            repo, main_path, pross.path)
        # create microservice instance
        created_mic_svc = object_creator(returned_pom_content, returned_yaml)
        
        #append the microservice object to list
        microservice_list.append(created_mic_svc)
        
    return microservice_list

