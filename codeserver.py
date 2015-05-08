
def codepool(codelist):
    codestring = []
    for code in codelist:
        codestring.append("import " + code + "\n")
    
    return "".join(codestring)    

def codespace(codestring):
    dict = {}
    exec(codestring) in dict
    return dict

class codeserver():
    """
    a codeserver object, gets initialized by a list of string names
    of importable python modules; They serve as our codespace.
    A codeserver object, is able to evaluate strings of
    expressions within the namespace of each code module within codelist.
    This is achived using get_val method of the codeserver instance (see
    its documentation).
    """
    
    def __init__(self, codelist):
        self.codelist = codelist
        self.codespace = codespace(codepool(self.codelist))

    def get_val(self, code, expr_string):
        """
        expr_string: should be a valid string expression
        code: is the string name;  should be in self.codelist. 
        expr_string gets evaluated within the code environment; the value
        gets returned
        """
        if not (code in self.codelist):
            return "%s is not known in codelist!" % code
        else:
            try: 
                return eval(expr_string, self.codespace[code].__dict__)
            except:
                return "Somthing wrong with your request!"

    def assert_equal(self, code, exp1, exp2):
        """
        Returns True if exp1 == exp2 within code namespace; otherwise
        returns False
        """
        return self.get_val(code, exp1) == self.get_val(code, exp2)

