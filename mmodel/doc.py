"""Functions that parse the graph and model description"""

def parse_description_graph(des_list):
    """Parse description list to display in graph
    
    The line breaks use '\l' to make sure they align left
    """

    des_str_list = []

    for name, content in des_list:
        des_str_list.append(f"{name}: {content}\l")

    return ''.join(des_str_list)


def attr_to_doc(attr_dict):
    """Parse description list to display in graph
    
    The line breaks use '\l' to make sure they align left
    """

    attr_str_list = []

    for name, content in attr_dict.items():
        attr_str_list.append(f"{name.upper()} - {content}\n")

    return ''.join(attr_str_list).expandtabs(4)
