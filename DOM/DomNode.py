class DomNode:
    __slots__ = ('attributes', 'child_nodes', 'node_name', 'node_type', 'node_value', 'parent_node', 'tagName',
                 'visual_cues')

    def __init__(self, node_type):
        self.attributes = dict()
        self.child_nodes = []
        self.node_name = None
        self.node_type = node_type
        self.node_value = None
        self.parent_node = None
        self.visual_cues = dict()

    '''
    Specify the node that contains HTML tag. For element nodes, the returned value is the tagName
    @param tagName 
    '''
    def createElement(self, tag_name):
        self.node_name = tag_name

    '''
    Specify the node that contains only text without any HTML tag. For text nodes, the returned value is "#text"
    @param nodeValue 
    @param parentNode
    '''
    def createTextNode(self, node_value, parent_node):
        self.node_name = '#text'
        self.node_value = node_value
        self.parent_node = parent_node

    '''
    Set the attributes to Dom node
    @param attributes 
    '''
    def setAttributes(self, attributes):
        self.attributes = attributes

    '''
    Set Set the visual information of web page to Dom Node.
    @param visual_cues 
    '''
    def setVisualCues(self, visual_cues):
        self.visual_cues = visual_cues

    '''
    Append the child nodes to its parent node
    @param childNode
    '''
    def appendChild(self, child_node):
        self.child_nodes.append(child_node)

    def __str__(self):
        return f'Node Type: {self.node_type} \
            \nNode Name: {self.node_name} \
            \nNode Value: {self.node_value} \
            \nVisual Cues: {self.visual_cues} \
            \nAttributes: {self.attributes} \
            \nChild Nodes: {self.child_nodes}'
