# 4.1 Visual Block Extraction
# Heuristic rules in block extraction phase


class BlockRule:
    threshold_width = 80
    threshold_height = 80

    '''
    <TABLE> and <P> are used only for organization purpose and are not appropriate to represent a single 
    visual block. In these cases, the current node should be further divided and replaced by its children.
    @param block (DOM)
    @return True if node is dividable., False otherwise.  
    '''
    @staticmethod
    def dividable(block):
        box = block.boxes[0]

        # Return False if node type is 3 (Text Node), because text node cannot be dividable anymore
        if box.node_type == 3:
            return False
        else:
            # Return False if detect image
            if box.node_name == 'img':
                return False
            else:
                if not BlockRule.isInlineNode(box.node_name):
                    return BlockRule.inlineRules(block)
                elif box.node_name == 'table':
                    return BlockRule.tableRules(block)
                elif box.node_name == 'tr':
                    return BlockRule.trRules(block)
                elif box.node_name == 'td':
                    return BlockRule.tdRules(block)
                elif box.node_name == 'p':
                    return BlockRule.pRules(block)
                else:
                    return BlockRule.otherRules(block)

    '''
    Different rules for Inline Text Node
    @param block
    @return True if one of rules success and node is dividable., False otherwise.  
    '''
    @staticmethod
    def inlineRules(block):
        if BlockRule.rule1(block):
            return True
        if BlockRule.rule2(block):
            return True
        if BlockRule.rule3(block):
            return True
        if BlockRule.rule4(block):
            return True
        if BlockRule.rule5(block):
            return True
        if BlockRule.rule6(block):
            return True
        if BlockRule.rule7(block):
            return True
        if BlockRule.rule9(block):
            return True
        if BlockRule.rule10(block):
            return True
        if BlockRule.rule12():
            return True
        return False

    '''
    Different rules for <TABLE> node
    @param block
    @return True if one of rules success and node is dividable., False otherwise.  
    '''
    @staticmethod
    def tableRules(block):
        if BlockRule.rule1(block):
            return True
        if BlockRule.rule2(block):
            return True
        if BlockRule.rule3(block):
            return True
        if BlockRule.rule8(block):
            return True
        if BlockRule.rule10(block):
            return True
        if BlockRule.rule13(block):
            return True
        return False

    '''
    Different rules for <TR> node
    @param block
    @return True if one of rules success and node is dividable., False otherwise.  
    '''
    @staticmethod
    def trRules(block):
        if BlockRule.rule1(block):
            return True
        if BlockRule.rule2(block):
            return True
        if BlockRule.rule3(block):
            return True
        if BlockRule.rule7(block):
            return True
        if BlockRule.rule8(block):
            return True
        if BlockRule.rule10(block):
            return True
        if BlockRule.rule13(block):
            return True
        return False

    '''
    Different rules for <TD> node
    @param block
    @return True if one of rules success and node is dividable., False otherwise.  
    '''
    @staticmethod
    def tdRules(block):
        if BlockRule.rule1(block):
            return True
        if BlockRule.rule2(block):
            return True
        if BlockRule.rule3(block):
            return True
        if BlockRule.rule4(block):
            return True
        if BlockRule.rule9(block):
            return True
        if BlockRule.rule10(block):
            return True
        if BlockRule.rule11(block):
            return True
        if BlockRule.rule13(block):
            return True
        return False

    '''
    Different rules for <P> node
    @param block
    @return True if one of rules success and node is dividable., False otherwise.  
    '''
    @staticmethod
    def pRules(block):
        if BlockRule.rule1(block):
            return True
        if BlockRule.rule2(block):
            return True
        if BlockRule.rule3(block):
            return True
        if BlockRule.rule4(block):
            return True
        if BlockRule.rule5(block):
            return True
        if BlockRule.rule6(block):
            return True
        if BlockRule.rule7(block):
            return True
        if BlockRule.rule9(block):
            return True
        if BlockRule.rule10(block):
            return True
        if BlockRule.rule12():
            return True
        return False

    '''
    Different rules for other nodes
    @param block
    @return True if one of rules success and node is dividable., False otherwise.  
    '''
    @staticmethod
    def otherRules(block):
        if BlockRule.rule1(block):
            return True
        if BlockRule.rule2(block):
            return True
        if BlockRule.rule3(block):
            return True
        if BlockRule.rule4(block):
            return True
        if BlockRule.rule6(block):
            return True
        if BlockRule.rule7(block):
            return True
        if BlockRule.rule9(block):
            return True
        if BlockRule.rule10(block):
            return True
        if BlockRule.rule12():
            return True
        return False

    '''
    Rule 1: If the DOM node is not a text node and it has no valid children, then this node cannot be
            divided and will be cut.
    @param block
    @return True if rule is applied, False otherwise.
    '''
    @staticmethod
    def rule1(block):
        node = block.boxes[0]

        if not BlockRule.isTextNode(node) and not BlockRule.hasValidChildren(node):
            print('Violated Rule 1, do not divide')
            block.isDividable = False
            # print(f'block.isDividable: {block.isDividable}')
            return False
        print('Comply Rule 1, divide')
        return True

    '''
    Rule 2: If the DOM node has only one valid child and the child is not a text node, then divide this node.
    @param block
    @return True if rule is applied, False otherwise
    '''
    @staticmethod
    def rule2(block):
        if len(block.children) == 1:
            node = block.children[0].boxes[0]
            if BlockRule.isValidNode(node) and not BlockRule.isTextNode(node):
                print('Comply Rule 2, divide')
                return True
        print('Violated Rule 2, do not divide')
        return False

    '''
    Rule 3: If the DOM node is the root node of the sub-DOM tree (corresponding to the block),
            and there is only one sub DOM tree corresponding to this block, divide this node.
    @param block
    @return True if rule is applied, False otherwise.  
    '''
    @staticmethod
    def rule3(block):
        node = block.boxes[0]
        count = 0

        for b_child in block.children:
            if b_child.boxes[0].node_name == node.node_name:
                result = True
                BlockRule.isOnlyOneDomSubTree(node, b_child.boxes[0], result)
                if result:
                    count += 1

        if count == 1:
            print('Comply Rule 3, divide')
            return True
        else:
            print('Violated Rule 3, do not divide')
            return False

    '''
     Rule 4: If all of the child nodes of the DOM node are text nodes or virtual text nodes, do not divide the node.
             * If the font size and font weight of all these child nodes are same, set the DoC of the extracted block
               to 10.
             * Otherwise, set the DoC of this extracted block to 9.
    @param block
    @return True if rule is applied, False otherwise.
    '''
    @staticmethod
    def rule4(block):
        node = block.boxes[0]
        sub_box_list = node.child_nodes
        count = 0

        if not sub_box_list:
            return False

        for box in sub_box_list:
            if BlockRule.isTextNode(box) or BlockRule.isVirtualTextNode(box):
                count += 1

        if len(sub_box_list) == count:
            block.isDividable = False
            block.isVisualBlock = True
            # print(f'block.isDividable: {block.isDividable}, block.isVisualBlock: {block.isVisualBlock}')

            font_size = 0
            font_weight = None
            for box in sub_box_list:
                child_font_size = box.visual_cues['font-size']
                child_font_weight = box.visual_cues['font-weight']
                if (font_size != 0 and font_size != child_font_size) or (
                        font_weight is not None and font_weight != child_font_weight):
                    block.DoC = 9
                    # block.doc(9)
                    # print(block.doc())
                    print('Violated Rule 4, do not divide')
                    return False
                else:
                    font_size = child_font_size
                    font_weight = child_font_weight
            block.DoC = 10
            # print(block.DoC)
            # block.doc(10)
            # print(block.doc())
            print('Violated Rule 4, do not divide')
            return False
        print('Comply Rule 4, divide')
        return True

    '''
    Rule 5: If one of the child nodes of the DOM node is line-break node, then divide this DOM node.
    @param block
    @return True if rule is applied, False otherwise.
    '''
    @staticmethod
    def rule5(block):
        node = block.boxes[0]
        sub_box_list = node.child_nodes

        if not sub_box_list:
            return False

        for box in sub_box_list:
            if not BlockRule.isInlineNode(box.node_name):
                print('Comply Rule 5, divide')
                return True
        print('Violated Rule 5, do not divide')
        return False

    '''
    Rule 6: If one of the child nodes of the DOM node has HTML tag <HR>, then divide this DOM node.
    @param block
    @return True if rule is applied, False otherwise.
    '''
    @staticmethod
    def rule6(block):
        node = block.boxes[0]
        sub_box_list = node.child_nodes

        if not sub_box_list:
            return False

        for box in sub_box_list:
            if box.node_name == 'hr':
                print('Comply Rule 6, divide')
                return True
        print('Violated Rule 6, do not divide')
        return False

    '''
    Rule 7: If the sum of all the child nodes' size is greater than this DOM node's size, then divide this node.
    @param block
    @return True if rule is applied, False otherwise.
    '''
    @staticmethod
    def rule7(block):
        node = block.boxes[0]
        sub_box_list = node.child_nodes

        if not sub_box_list:
            return False

        # Size of DOM node
        x = node.visual_cues['bounds']['x']
        y = node.visual_cues['bounds']['y']
        width = node.visual_cues['bounds']['width']
        height = node.visual_cues['bounds']['height']
        area = abs(((x + width) - x) * ((y + height) - y))

        # Use loop to compare with child nodes
        for box in sub_box_list:
            child_x = box.visual_cues['bounds']['x']
            child_y = box.visual_cues['bounds']['y']
            child_width = box.visual_cues['bounds']['width']
            child_height = box.visual_cues['bounds']['height']
            child_area = abs(((child_x + child_width) - child_x) * ((child_y + child_height) - child_y))

            if child_area > area:
                print('Comply Rule 7, divide')
                return True
        print('Violated Rule 7, do not divide')
        return False

    '''
    Rule 8: If the background color of this node is different from one of its children's, divide this node and at the
            same time, the child node with different background color will not be divided in this round.
            * Set the DoC value (6-8) for the child node based on the html tag of the child node and the size of
              the child node.
    @param block
    @return True if rule is applied, False otherwise.
    '''
    @staticmethod
    def rule8(block):
        node = block.boxes[0]
        bg_color = node.visual_cues['background-color']

        for ele in block.children:
            child = ele.boxes[0]
            child_bg_color = child.visual_cues['background-color']
            if bg_color != child_bg_color:
                block.isDividable = False
                block.isVisualBlock = True
                # print(f'block.isDividable: {block.isDividable}, block.isVisualBlock: {block.isVisualBlock}')
                block.DoC = 7
                # print(block.DoC)
                print('Comply Rule 8, divide')
                return True
        print('Violated Rule 8, do not divide')
        return False

    '''
    Rule 9: If the node has at least one text node child or at least one virtual text node child, and the node's
            relative size is smaller than a threshold, then the node cannot be divided.
            * Set the DoC value (from 5-8) based on the html tag of the node.
    @param block
    @return True if rule is applied, False otherwise.
    '''
    @staticmethod
    def rule9(block):
        node = block.boxes[0]
        sub_box_list = node.child_nodes
        count = 0

        if not sub_box_list:
            print('Violated Rule 9, do not divide')
            return False

        for box in sub_box_list:
            if BlockRule.isTextNode(box) or BlockRule.isVirtualTextNode(box):
                count += 1

        relative_size = node.visual_cues['bounds']['x'] * node.visual_cues['bounds']['y']
        threshold = BlockRule.threshold_width * BlockRule.threshold_height
        if count >= 1 and relative_size < threshold:
            block.isDividable = False
            block.isVisualBlock = True
            # print(f'block.isDividable: {block.isDividable}, block.isVisualBlock: {block.isVisualBlock}')
            if node.node_name == 'xdiv':
                block.DoC = 6
                # block.doc(6)
            elif node.node_name == 'code':
                block.DoC = 6
            elif node.node_name == 'div':
                block.DoC = 5
            else:
                block.DoC = 8

            # print(block.DoC)
            print('Violated Rule 9, do not divide')
            return False
        print('Comply Rule 9, divide')
        return True

    '''
    Rule 10: If the child of the node with maximum size are smaller than a threshold (relative size), do not divide
             this node.
             * Set the DoC based on the html tag and size of this node.
    @param block
    @return True if rule is applied, False otherwise.
    '''
    @staticmethod
    def rule10(block):
        node = block.boxes[0]
        sub_box_list = node.child_nodes
        maximum = 0

        if not sub_box_list:
            return False

        for box in sub_box_list:
            child_size = box.visual_cues['bounds']['x'] * box.visual_cues['bounds']['y']
            maximum = child_size if maximum < child_size else maximum

        if maximum < BlockRule.threshold_width * BlockRule.threshold_height:
            block.isDividable = False
            block.isVisualBlock = True
            # print(f'block.isDividable: {block.isDividable}, block.isVisualBlock: {block.isVisualBlock}')

            if node.node_name == 'xdiv':
                block.DoC = 6
            elif node.node_name == 'a':
                block.DoC = 7
            elif node.node_name == 'div':
                block.DoC = 5
            else:
                block.DoC = 8
            print('Violated Rule 10, do not divide')
            return False
        print('Comply Rule 10, divide')
        return True

    '''
    Rule 11: If previous sibling node has not been divided, do not divide this node.
    @param block
    @return True if rule is applied, False otherwise.
    '''
    @staticmethod
    def rule11(block):
        children = block.parent.children
        index = children.index(block)
        count = 0

        for i in range(index):
            if not children[i].isDividable:
                count += 1

        if count == index:
            print('Violated Rule 11, do not divide')
            return False
        print('Comply Rule 11, divide')
        return True

    '''
    Rule 12: Divide this node.
    @return True.
    '''
    @staticmethod
    def rule12():
        return True

    '''
    Rule 13: Do not divide this node.
             * Set the DoC value based on the html tag and size of this node.
    @param block
    @return True if rule is applied, False otherwise.
    '''
    @staticmethod
    def rule13(block):
        node = block.boxes[0]
        block.isDividable = False
        block.isVisualBlock = True
        # print(f'block.isDividable: {block.isDividable}, block.isVisualBlock: {block.isVisualBlock}')

        if node.node_name == 'xdiv':
            block.DoC = 6
        elif node.node_name == 'li':
            block.DoC = 7
        elif node.node_name == 'span':
            block.DoC = 7
        elif node.node_name == 'img':
            block.DoC = 7
        elif node.node_name == 'sup':
            block.DoC = 7
        else:
            block.DoC = 8
        print('Violated Rule 13, do not divide')
        return False

    '''
    Here are the inline elements in HTML:
    Reference: https://www.w3schools.com/html/html_blocks.asp#:~:text=An%20inline%20element%20does%20not%20start%20on%20a%20new%20line,span%3E%20element%20inside%20a%20paragraph.
    @param element
    @return True if node is inline node, False otherwise.
    '''
    @staticmethod
    def isInlineNode(element):
        if (element == 'a' or
                element == 'abbr' or
                element == 'acronym' or
                element == 'b' or
                element == 'bdo' or
                element == 'big' or
                element == 'br' or
                element == 'button' or
                element == 'cite' or
                element == 'code' or
                element == 'dfn' or
                element == 'em' or
                element == 'i' or
                element == 'img' or
                element == 'input' or
                element == 'kbd' or
                element == 'label' or
                element == 'map' or
                element == 'object' or
                element == 'q' or
                element == 'samp' or
                element == 'script' or
                element == 'select' or
                element == 'small' or
                element == 'span' or
                element == 'strong' or
                element == 'sub' or
                element == 'sup' or
                element == 'textarea' or
                element == 'time' or
                element == 'tt' or
                element == 'var'):
            return False
        else:
            return True

    '''
    Valid node: a node that can be seen through the browser. The node’s width and height are not equal to zero.
    @param node
    @return True if node is valid, False otherwise.
    '''
    @staticmethod
    def isValidNode(node):
        display = node.visual_cues['display']
        visibility = node.visual_cues['visibility']
        height = node.visual_cues['bounds']['height']
        width = node.visual_cues['bounds']['width']

        if display == 'none' or visibility == 'hidden' or height == '0px' or width == '0px':
            return False
        return True

    '''
    Text node: the DOM node corresponding to free text, which does not have html tag.
    @param node
    @return True if node is text node, False otherwise.
    '''
    @staticmethod
    def isTextNode(node):
        return node.node_type == 3

    '''
    Virtual text node (recursive definition):
    * Inline node with only text node children is a virtual text node.
    * Inline node with only text node and virtual text node children is a virtual text node.
    @param node
    @return True if node is virtual text node, False otherwise.
    '''
    @staticmethod
    def isVirtualTextNode(node):
        sub_box_list = node.child_nodes
        count = 0

        if not sub_box_list:
            return False

        for box in sub_box_list:
            if BlockRule.isTextNode(box) or BlockRule.isVirtualTextNode(box):
                count += 1

        if count == len(sub_box_list):
            return True
        return False

    '''
    Checks if node's subtree is unique in DOM tree.
    @param pattern for comparing
    @param node from DOM tree
    @param result True if node is unique otherwise false
    '''

    @staticmethod
    def isOnlyOneDomSubTree(pattern, node, result):
        if pattern.node_name != node.node_name:
            return False
        elif len(pattern.child_nodes) != len(node.child_nodes):
            return False
        elif not result:
            return
        else:
            for i in range(len(pattern.child_nodes)):
                BlockRule.isOnlyOneDomSubTree(pattern.child_nodes[i], node.child_nodes[i], result)

    '''
    Check if node has valid children.
    @param node
    @return True if valid children is found, False otherwise.
    '''
    @staticmethod
    def hasValidChildren(node):
        sub_box_list = node.child_nodes

        for box in sub_box_list:
            if BlockRule.isValidNode(box):
                return True
        return False
