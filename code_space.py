#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    import subprocess32 as sbp
except:
    import subprocess as sbp

import os.path as osp
import time
import codecs
import re

def get_encoding(module):
    """
    returns the encoding of the source-file of python module.
    if it is not unsuccessful returns utf-8 (last chance! :)
    """
    module_path = osp.abspath(module.__file__)
    oo = open(module_path, "rb")
    encoding_pattern = re.compile(r"^.*?coding[:=]\s*([-\w.]+)") 
    i = 1
    encoding = None 
    while i <= 3: 
        line = oo.readline()
        result = re.match(encoding_pattern, line)  
        try:
            return result.group(1)
        except:
            i += 1
                
    if encoding == None: return "utf-8"


def server_code_generator(server_module, import_list = ["code2"]):
    """writes a file identical to server_module (which is a literal name of
    an imported module) in the same directory as server_module, after first
    importing all the modules from import_list.
    import_list should be a list of string names of the importable
    python modules (without .py).
    It returns the string name of the generated python module; 
    it is of this format:
     sever_module_year_month_day_hour_min.py
    """

    now = time.gmtime(time.time())
    now_str = '_'.join([str(now.tm_year), str(now.tm_mon),\
                        str(now.tm_mday), str(now.tm_hour),\
                        str(now.tm_min)]) 
      
    server_path = osp.abspath(server_module.__file__)
    new_server_path = '_'.join([osp.splitext(server_path)[0], now_str])\
                      + '.py'

    encoding = get_encoding(server_module) 
    server_file = codecs.open(server_path, "r", encoding)
    new_server_file = codecs.open(new_server_path, "w", encoding) 
    
    new_server_file.write("#!/usr/bin/python\n")
    new_server_file.write("# -*- coding: " + encoding  + " -*-\n")

    for item in import_list:
        new_server_file.write("import " + item + '\n')
    
    for line in server_file.readlines():
        if not (("!/" in line) or ("# -*-" in line)): 
            new_server_file.write(line)
    
    server_file.close()
    new_server_file.close()
    
    return str(new_server_path)


class name_space():
    """A name_sapce through which all
    the objects contained in the code_list 
    are available without conflicting eachother.
    code_list is a list of names of importable pure 
    python files (i.e., either python modules or a python
    file on the path).
    """
    def __init__(self, code_list):
        """
        initializes the object_bank
        """
        self.object_bank = object_bank(code_list)
