#!/usr/bin/python

import traceback as tb
import re
import os
import sys
from contextlib import contextmanager
from tempfile import NamedTemporaryFile


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




class repl(object):
    """
    these attributes keeps the state of repl for user at basically three
    different levels:
        level 1: user information
            user, group, session, encoding
        level 2: repl interaction state with user
            bufer, blank_line, evaluation, fille
        level 3: repl interaction with python interpreter
            glob, codepath
    """
    def __init__(self, user, session, group = "Guest", bufer = [], encoding = 'utf-8', codepath = None):
        self.user = user
        self.group = group
        self.session = session
        self.bufer = bufer
        self.blank_line = 0
        self.evaluation = True #An internal variable to keep track if the current buffer, to be executed, should be eval-ed or exec-ed
        fille = NamedTemporaryFile(mode = 'w+t', delete = False)
        self.encoding = encoding
        self.fille = fille.name 
        self.glob = {}
        self.codepath = codepath
        if self.codepath != None: 
            if os.path.exists(self.codepath) and self.codepath.endswith(".py"):
                f = open(codepath, "r")
                exec(f) in self.glob
                self.send(u'\n')
                f.close()    
            else: 
                raise IOError("the codepath is not a valid python file")    
    
    def __del__(self):
        os.remove(self.fille)

    def _reset_after_flush_bufer(self):
        """
        Resets the state varibales to the initial values
        after flushing the bufer statements
        """
        self.bufer = []
        self.blank_line = 0
        self.evaluation = True

    def send(self, statement):
        """
        returns the result of execution or evaluation of the statement in
        byte string encoded with self.encoding. 
        every statement should be in unicode, and should be ended with "\n".
        all the statements are executed or evaluated (whichever is 
        applicable for the statement) within the global environment of the
        user (self.glob).
        It immulates the behaviour of the standard python repl.
        For example sending u'def f():' returns '...', it does not evaluate
        or execute the statement and waits for the whole block of function 
        definition to be completed. At the end of completion of function
        defition the whole body of function will be executed within the 
        global environment of the user. On the other hand, this is different
        from repl as you can send multiple lines into it to be executed in
        python, the end-python return will be returned to you.
        """
        if not statement.endswith(u'\n'):
            statement += u'\n'

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
                statement += u'\n'
                io = self.IO(statement)
                if io == u'':
                    return u'>>> '.encode(self.encoding)
                else:
                    return u''.join([io, u'>>> ']).encode(self.encoding)
            else:
                return u'... '.encode(self.encoding)
        else:
            statement = u''.join(self.bufer)
            self._reset_after_flush_bufer()
            statement += u'\n'
            io = self.IO(statement)
            if io == u'':
                return u'>>> '.encode(self.encoding)
            else:
                return u''.join([io, u'>>> ']).encode(self.encoding)

    def IO(self, command):
        """
        Executes command in the self.glob, meanwhile redirects python 
        interpretor stdout into self.fille. 
        """
        if self.evaluation:
            try: 
                with open(self.fille, 'w') as f, stdout_redirected(f):
                    if command.startswith(u'print') or \
                            (ends_with(command,  u')') and 
                                    not command.startswith(u'(')):
                        exec(command, self.glob, None)
                    else:
                        exec(u''.join([u'print ', command]), self.glob, None)
            except SyntaxError:
                try: 
                    with open(self.fille, 'w') as f, stdout_redirected(f):
                        exec(command, self.glob, None)
                except:
                    with open(self.fille, 'w') as f, stdout_redirected(f):
                        tb.print_exc(limit=0, file = f)
            except:
                with open(self.fille, 'w') as f, stdout_redirected(f):
                    tb.print_exc(limit=0, file = f)
        else: 
            try: 
                with open(self.fille, 'w') as f, stdout_redirected(f):
                    exec(command, glob, None)
            except:
                with open(self.fille, 'w') as f, stdout_redirected(f):
                    tb.print_exc(limit=0, file = f)

        with open(self.fille, 'r') as f:
            data = f.read()
        
        return data

    
