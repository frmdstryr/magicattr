"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE, distributed with this software.

Created on June, 2018
"""
import ast
import sys
from functools import reduce


#: Types of AST nodes that are used
_AST_TYPES = (ast.Name, ast.Attribute, ast.Subscript, ast.Call)
_STRING_TYPE = basestring if sys.version_info.major == 2 else str


def get(obj, attr):
    """ A getattr that supports nested lookups on objects, dicts, lists, and
    any combination in between.
    
    Parameters
    ---------
    obj: Object
        An object to lookup the attribute on
    attr: String
        A attribute string to lookup
        
    Returns
    -------
    result: Object
        The object retrieved
    """
    return reduce(_lookup, _parse(attr), obj)


def set(obj, attr, val):
    """ A setattr that supports nested lookups on objects, dicts, lists, and
    any combination in between.
    
    Parameters
    ---------
    obj: Object
        An object to lookup the attribute on
    attr: String
        A attribute string to lookup
    val: Object
        The value to set
        
    """
    nodes = tuple(_parse(attr))
    if len(nodes) > 1:
        obj = reduce(_lookup, nodes[:-1], obj)
        node = nodes[-1]
    else:
        node = nodes[0]

    if isinstance(node, ast.Attribute):
        return setattr(obj, node.attr, val)
    elif isinstance(node, ast.Subscript):
        obj[_lookup_subscript_value(node.slice.value)] = val
        return
    elif isinstance(node, ast.Name):
        return setattr(obj, node.id, val)
    raise NotImplementedError("Node is not supported: %s" % node)


def delete(obj, attr):
    """ A delattr that supports deletion of a nested lookups on objects, 
    dicts, lists, and any combination in between.
    
    Parameters
    ---------
    obj: Object
        An object to lookup the attribute on
    attr: String
        A attribute string to lookup
    """
    nodes = tuple(_parse(attr))
    if len(nodes) > 1:
        obj = reduce(_lookup, nodes[:-1], obj)
        node = nodes[-1]
    else:
        node = nodes[0]

    if isinstance(node, ast.Attribute):
        return delattr(obj, node.attr)
    elif isinstance(node, ast.Subscript):
        del obj[_lookup_subscript_value(node.slice.value)]
        return
    elif isinstance(node, ast.Name):
        return delattr(obj, node.id)
    raise NotImplementedError("Node is not supported: %s" % node)


def _parse(attr):
    """ Parse and validate an attr string 
    
    Parameters
    ----------
    attr: String
    
    Returns
    -------
    nodes: List
        List of ast nodes
    
    """
    if not isinstance(attr, _STRING_TYPE):
        raise TypeError("Attribute name must be a string")
    nodes = ast.parse(attr).body
    if not nodes or not isinstance(nodes[0], ast.Expr):
        raise ValueError("Invalid expression: %s"%attr)
    return reversed([n for n in ast.walk(nodes[0])
                     if isinstance(n, _AST_TYPES)])


def _lookup_subscript_value(node):
    """ Lookup the value of ast node on the object.
    
    Parameters
    ---------
    obj: Object
        An object to lookup the attribute, index, or key
    node: ast.Attribute, ast.Name, or ast.Subscript
        Node to lookup
        
    Returns
    -------
    result: Object
        The object retrieved
    """
    # Handle indexes
    if isinstance(node, ast.Num):
        return node.n
    # Handle string keys
    elif isinstance(node, ast.Str):
        return node.s
    # Handle negative indexes
    elif (isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub)
          and isinstance(node.operand, ast.Num)):
        return -node.operand.n
    raise NotImplementedError("Subscript node is not supported: "
                              "%s" % ast.dump(node))


def _lookup(obj, node):
    """ Lookup the given ast node on the object.
    
    Parameters
    ---------
    obj: Object
        An object to lookup the attribute, index, or key
    node: ast.Attribute, ast.Name, or ast.Subscript
        Node to lookup
        
    Returns
    -------
    result: Object
        The object retrieved
    """
    if isinstance(node, ast.Attribute):
        return getattr(obj, node.attr)
    elif isinstance(node, ast.Subscript):
        return obj[_lookup_subscript_value(node.slice.value)]
    elif isinstance(node, ast.Name):
        return getattr(obj, node.id)
    elif isinstance(node, ast.Call):
        raise ValueError("Function calls are not allowed.")
    raise NotImplementedError("Node is not supported: %s" % node)
