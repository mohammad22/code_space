
def codepool(codelist):
    codestring = []
    for code in codelist:
        codestring.append("import " + code + "\n")
    
    return "".join(codestring)    

def codespace(codestring):
    """ given a list of code strings, returns the namespace dictionary of 
    the executed codes within codestring
    """
    dict = {}
    exec(codestring) in dict
    return dict

def init_locals(clients):
    dict = {}
    for client in clients: dict[client] = {}
    return dict

import re
pattern = re.compile(r".*import", re.DOTALL)

class codeserver():
    """
    a codeserver object, gets initialized by a list of string names
    of importable python modules; They serve as our codespace.
    A codeserver object, is able to evaluate strings of expressions within
    the namespace of each client (as local) and code module within the 
    codelist (as global). This is achived using get_val method of the 
    codeserver instance (see its documentation).
    """
    
    def __init__(self, codelist, clients):
        self.codelist = codelist
        self.codespace = codespace(codepool(self.codelist))
        self.clients = clients
        self.clients_locals = init_locals(self.clients)
        self.exps_expr = {}
   
    def get_val(self, code, client, expr):
        """
        expr: should be a valid string expression
        code: is the string name;  should be in self.codelist; refers
        to the global namesapce which expr will be evaluated against. 
        expr gets evaluated withingt the code context as global and
        the locals of cleint namespace; the value gets returned
        client: is a string name (should be in self.clients); 
        """
        if not (code in self.codelist):
            return "%s is not known in codelist!" % code
        elif not (client in self.clients):
            return "%s is not known in clients list!" % client
        elif not pattern.match(expr) == None: 
            return "You can not use import."
        else:
            try: 
                return eval(expr, self.codespace[code].__dict__,\
                            self.clients_locals[client])
            except:
                try:
                 exec(expr, self.codespace[code].__dict__,\
                            self.clients_locals[client])
                except:
                    return "Somthing's wrong!"

    def assert_equal(self, code, exp1, exp2):
        """
        Returns True if exp1 == exp2 within code namespace; otherwise
        returns False
        """
        return self.get_val(code, exp1) == self.get_val(code, exp2)


