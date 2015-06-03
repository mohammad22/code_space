import os.path as osp


def codespace(codepath):
    """ given a file path codepath, returns a dictionary codepath: dict,
    (dict: the dictionary of the executed code in codepath). 
    returns None if codepath is not valid.
    """
    dict = {}
    f = open(codepath, "r")
    exec(f) in dict
    return dict

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
    codelist (as global). 
    two main attributes are self.pathlist, self.clients:
    self.pathlist: a list of path of python files (accessible to the 
    program) which serve as global namespace such that clients codes
    will be evaluated against them.
    self.clients: a list of unique strings representing each client 
    (conisdered as client id).
    The main method is get-val(self, path, client, expr)
    it returns the value of the string expr, aagainst the global namesspace
    of path (should be in self.pathlist) for the client (should be in
    self.clients). This is a safe evaluation: it can not block the python
    interpretor for more than one second; it can not touch the global 
    namespace, so several clients have access to the same global namespace
    at the same time without interfering. Restrictions: this only works 
    for evaluation expression strings, so basically client codes can not 
    define any new python object for itself; this means this is not useful
    to evaluate clients codes which are arbitrary python codes. This is best
    suited for reach codespace (already provided in pathlist) in which one
    linear python codes should be evaluated against; like a test or 
    excercise session for a class lab, and student reponses as clients 
    codes 
    """
    
    def __init__(self, pathlist, clients):
        self.pathlist = pathlist
        self.codelist = {}
        self.clients = clients
        self.clients_locals = init_locals(self.clients)
        self.clients_globals = {'client': {}} 
    
    def check_pathlist(self):
        """
        Checks the health of every path in the pathlist, and complains
        if each one of them is not accessible. 
        """
        for i in range(len(self.pathlist) - 1):
            path = self.pathlist[i]
            if not( osp.isfile(path) and osp.splitext(path)[1] == ".py"):
                print "%s is not valid. it is  deleted from the pathlist.\
                        You can modify pathlist like any other python list\
                        at any time.\ \n" % path
                del self.pathlist[i]
    
    def check_clients(self):
        for i in range(len(self.clients) - 1):
            client = self.clients[i]
            if not isinstance(clien, str): 
                print "%s is not a valid string. it is delted from clients.\
                You can modify the clients list like any other python list\
                at any time." % client
                del self.clients[i]

    def codespace(self, codeowner, path):
        """The main interface to self.code_space and self.clients_globals.
        codeowner = 'global' if it is not 'client'.
        """ 
        if path in self.pathlist:
            if codeowner == 'global':
                return codepool(self.codelist, path)
            elif codeowner == 'client':
                return codepool(self.clients_globals[codeowner], path)
            else:
                print "%s is not valid!" % codeowner
                return None
        else:
            print "%s is not valid!" % path
            return None

    def pass_healthy_val(self, val, path, client):
        try:
            if self.codespace(client, path) ==\
                    self.codespace('global', path):
                return val
            else:
                del self.clients_globals[client][path]
                self.codespace(client, path)
                return "No access to global namespace!"
        except:
                return None

    def get_val(self, path, client, expr):
        """
        expr: should be a valid string expression 
        path: is the string name;  should be in self.pathlist; refers
        to the global namesapce which expr will be evaluated against;
        (within the code context as global and the locals of client 
        namespace); 
        the evaluated value gets returned; If not sucessful returns None. 
        client: a string name (should be in self.clients); 
        """
        if not (path in self.pathlist):
            return "%s is not known!" % path
        elif not (client in self.clients):
            return "%s is not valid client!" % client
        else:
            try:
                val = eval(expr, self.codespace('client', path), 
                        self.clients_locals[client])
                return self.pass_healthy_val(val, path, 'client')
            except:
                return "Unable to evaluate the code. try again!" 

    def assert_equal(self, code, exp1, exp2):
        """
        Returns True if exp1 == exp2 within code namespace; otherwise
        returns False
        """
        return self.get_val(code, exp1) == self.get_val(code, exp2)


