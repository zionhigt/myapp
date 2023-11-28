class Node:
    def __init__(self, parent, key, value=None):
        self.parent = parent
        self.key = key
        self.value = value
        self.children = []
    
    def __str__(self):
        return self.key[1]
    
    @property
    def params(self):
        if self.parent is not None:
            return [*self.parent.params, self.key[1]]
        return [self.key[1]]
    
    def append_child(self, key):
        child = self.get_child_by_key(key, True)
        if child is None:
            child = Node(self, key)
            self.children.append(child)
        return child

    def append_children(self, keys, verb, value):
        if isinstance(keys, str):
            keys = list(enumerate([i for i in keys.split("/") if i]))
        if len(keys):
            key = keys[0]
            child = self.append_child(key)
            return child.append_children(keys[1:], verb, value)
        if self.value is None:
            self.value = {}
        if self.value.get(verb) is None:
            self.value.update({
                verb: []
            })
        self.value[verb].append(value)
        return self

    def get_child_by_key(self, key, strict=False):
        fn_strict = lambda *args, **kwarg: False
        if not strict:
            fn_strict = lambda x: x.key[0] == key[0] and x.key[1][0] == ":"
        children = list(filter(lambda x: x.key == key or fn_strict(x), self.children))
        if len(children):
            return children[0]
    
    def search(self, route):
        list_path = route
        if isinstance(route, str):
            list_path = list(enumerate([i for i in route.split("/") if i]))
        if len(list_path):
            key = list_path[0]
            child = self.get_child_by_key(key)
            if child is not None:
                return child.search(list_path[1:])
        return self

class Controller:

    @staticmethod
    def get_instance():
        return Controller(Node(None, (-1, "/")))
    
    def __init__(self, node):
        self.node = node
        self._cache = {}

    def append_children(self, *args, **kwargs):
        return self.node.append_children(*args)
    
    def get_node(self, route):
        node = self._cache.get(route)
        if node is None:
            node = self.node.search(route)
            self._cache.update({
                route: node
            })
        return node