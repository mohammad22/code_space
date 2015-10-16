#!/usr/bin/python

import traceback as tb
import re
import os
import sys
from contextlib import contextmanager
import traceback


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

def fileno(file_or_fd):
    fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
    if not isinstance(fd, int):
        raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
    return fd

@contextmanager
def stdout_redirected(to=os.devnull, stdout=None):
    if stdout is None:
       stdout = sys.stdout

    stdout_fd = fileno(stdout)
    # copy stdout_fd before it is overwritten
    #NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied: 
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stdout_fd)  # $ exec >&to
        except ValueError:  # filename
            with open(to, 'wb') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
        try:
            yield stdout # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            #NOTE: dup2 makes stdout_fd inheritable unconditionally
            stdout.flush()
            os.dup2(copied.fileno(), stdout_fd)  # $ exec >&copied


def IO(command, path, glob = {}, evaluation = True):
    
    if evaluation:
        try: 
            with open(path, 'w') as f, stdout_redirected(f):
                if command.startswith(u'print') or \
                        (ends_with(command,  u')') and 
                                not command.startswith(u'(')):
                    exec(command, glob, None)
                else:
                    exec(u''.join([u'print ', command]), glob, None)
        except SyntaxError:
            try: 
                with open(path, 'w') as f, stdout_redirected(f):
                    exec(command, glob, None)
            except:
                with open(path, 'w') as f, stdout_redirected(f):
                    traceback.print_exc(limit=0, file = f)
        except:
            with open(path, 'w') as f, stdout_redirected(f):
                traceback.print_exc(limit=0, file = f)
    else: 
        try: 
            with open(path, 'w') as f, stdout_redirected(f):
                exec(command, glob, None)
        except:
            with open(path, 'w') as f, stdout_redirected(f):
                traceback.print_exc(limit=0, file = f)

    with open(path, 'r') as f:
        data = f.read()
    
    return data






class repl(object):
    """
    these attributes keeps the state of repl for user at basically three
    different levels:
    
    level 1: user information
    user, session, encoding

    level 2: repl interaction state with user
    bufer, blank_line, evaluation, fille

    level 3: repl interaction with python interpreter
    glob

    """

    def __init__(self, user, session, bufer = [], encoding = 'utf-8'):
        self.user = user
        self.session = session
        self.bufer = bufer
        self.blank_line = 0
        self.evaluation = True
        self.fille = "temp.txt" #this should be construced in a thread-safe
        self.glob = {}
        self.encoding = encoding
                                # manner

    def _reset_after_flush_bufer(self):
        """
        As it says, resets the state varibales to the initial values
        after flushing the bufer statements
        """
        self.bufer = []
        self.blank_line = 0
        self.evaluation = True



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
        
        if ends_with(statement, u'\n'): ## despite its name, this actually checks for statement to  be a blank line.
            self.blank_line += 1

        self.bufer.append(statement) ## from now on, self.bufer is the real statement we are dealing with.

        if ends_with(statement, u':'):
            return u'... '.encode(self.encoding)
        
        elif len(self.bufer) > 1:
            self.evaluation = False
            if self.blank_line == 1:
                statement = u''.join(self.bufer)
                self._reset_after_flush_bufer()
                io = IO(statement, self.fille, self.glob)
                if io == u'':
                    return u'>>> '.encode(self.encoding)
                else:
                    return u''.join([io, u'>>> ']).encode(self.encoding)
            else:
                return u'... '.encode(self.encoding)
        else:
            statement = u''.join(self.bufer)
            self._reset_after_flush_bufer()
            io = IO(statement, self.fille, self.glob, self.evaluation)
            if io == u'':
                return u'>>> '.encode(self.encoding)
            else:
                return u''.join([io, u'>>> ']).encode(self.encoding)


    
