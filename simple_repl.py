#!/usr/bin/python

import traceback as tb
import re
from commandio import IO



colon = re.compile(r'^.*[:]\r*\n+')
pure_line = re.compile(r'^ *\n+$')

def ends_with(string, character):
    
    patt = ''.join([u'^.*[', character, u']\r*\n+'])
    if character == u':':
        pattern = colon
    if character == u'\n':
        pattern = pure_line
    else:    
        pattern = re.compile(patt)

    if len(re.findall(pattern, string)) >= 1:
        return True
    else:
        return False


class repl(object):

    def __init__(self, user, session, bufer = [], encoding = 'utf-8'):
        self.user = user
        self.session = session
        self.bufer = bufer
        self.blank_line = 0
        self.encoding = encoding
        self.glob = {}
        self.evaluation = True
        self.fille = "temp.txt" #this should be construced in a thread-safe
                                # manner



    def send(self, statement):
        """
        sends statements and retunrs the result of execution
        or evaluation of the statement in byte string encoded 
        with self.encoding. 
        every statement should be in unicode, and should be ended with "\n".
        all the statements are executed or evaluated (whichever is 
        applicable for the statement) within the global environment of the
        user (self.glob).
        This method immulates the behaviour of the standard python repl.
        For example sending u'def f():' returns '...', it does not evaluate
        or execute the statement and waits for the whole block of function 
        definition to be completed. At the end of completion of function
        defition the whole body of function will be executed within the 
        global environment of the user (similar to repl), and the function
        will be available for later calls.
        """
        if not statement.endswith(u'\n'):
            statement = statement + u'\n'

        self.bufer.append(statement)
        
        if ends_with(statement, u'\n'): ## despite its name, this actually checks for statement to  be a blank line.
            self.blank_line += 1

        if ends_with(statement, u':'):
            return u'...'.encode(self.encoding)
        elif len(self.bufer) > 1:
            self.evaluation = False
            if self.blank_line == 1:
                statement = u''.join(self.bufer)
                self.bufer = []
                self.blank_line = 0
                io = IO(statement, self.fille, self.glob)
                if io == u'':
                    return u'>>>'.encode(self.encoding)
                else:
                    return io.encode(self.encoding)
            else:
                return u'...'.encode(self.encoding)
        else:
            self.bufer = []
            self.blank_line = 0
            io = IO(statement, self.fille, self.glob, self.evaluation)
            if io == u'':
                return u'>>>'.encode(self.encoding)
            else:
                return io.encode(self.encoding)


    
