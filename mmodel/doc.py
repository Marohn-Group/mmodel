"""Functions that parse the graph and model description"""

def parse_description_graph(des_list):
    """Parse description list to display in graph
    
    The line breaks use '\l' to make sure they align left
    """

    des_str_list = []

    for name, content in des_list:
        des_str_list.append(f"{name}: {content}\l")

    return ''.join(des_str_list)


def parse_description_doc(des_list):
    """Parse description list to display in graph
    
    The line breaks use '\l' to make sure they align left
    """

    des_str_list = []

    for name, content in des_list:
        tab_content = '\n\t'.join(content.split('\n'))
        des_str_list.append(f"{name.upper()}\n\t{tab_content}\n")

    return ''.join(des_str_list)
