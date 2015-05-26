import os.path as osp

def codespace(codepath):
    """ given a file path codepath, returns a dictionary codepath: dict,
    (dict: the dictionary of the executed code in codepath). 
    returns None if codepath is not valid.
    """
    if osp.isfile(codepath) and osp.splitext(codepath)[1] == ".py":
        dict = {}
        f = open(codepath, "r")
        exec(f) in dict
        return dict
    else:
        print "%s should be a valid python path!\n" % codepath 
        return None

def codepool(spacelist, path):
    try:
        return spacelist[path]
    except:
        spacelist[path] = codespace(path)
        return spacelist[path]


def init_locals(clients):
    dict = {}
    for client in clients: dict[client] = {}
    return dict

class codeserver():
    """
    a codeserver object, gets initialized by a list of paths
    of python codefiles; They serve as the codespace.
    A codesserver, is able to evaluate strings of expressions within
    the namespace of each client (as local) and code module within the 
    codelist (as global). This is achived using get_val method of the 
    codeserver instance (see its documentation).
    """
    
    def __init__(self, pathlist, clients):
        self.pathlist = pathlist
        self.codelist = {}
        self.clients = clients
        self.clients_locals = init_locals(self.clients)
        self.clients_globals = init_locals(self.clients) 
    
    def codespace(self, codeowner, path):
        """The main interface to self.code_space and self.clients_globals.
        codeowner = 'global' if it is not a client.
        """ 
        if path in self.pathlist:
            if codeowner == 'global':
                return codepool(self.codelist, path)
            elif codeowner in self.clients:
                return codepool(self.clients_globals[codeowner], path)
            else:
                print "%s is not valid!" % codeowner
                return None
        else:
            print "%s is not valid!" % path
            return None

    def get_val(self, path, client, expr):
        """
        expr: should be a valid string expression 
        code: is the string name;  should be in self.codelist; refers
        to the global namesapce which expr will be evaluated against;
        (within the code context as global and the locals of client 
        namespace); 
        the evaluated value gets returned; If not sucessful returns None. 
        client: is a string name (should be in self.clients); 
        """
        if not (path in self.pathlist):
            return "%s is not known!" % path
        elif not (client in self.clients):
            return "%s is not valid!" % client
        #elif not pattern.match(expr) == None: 
            #return "You can not use import."
        else:
            try:
                val = eval(expr, self.codespace(client, path), 
                        self.clients_locals[client])
                if self.codespace(client, path) ==\
                        self.codespace('global', path):
                    return val
                else:
                    del self.clients_globals[client][path]
                    self.codespace(client, path)
                    return None
            except:
                return None 


    def assert_equal(self, code, exp1, exp2):
        """
        Returns True if exp1 == exp2 within code namespace; otherwise
        returns False
        """
        return self.get_val(code, exp1) == self.get_val(code, exp2)


