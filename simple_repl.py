#!/usr/bin/python

import traceback as tb
import re


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

    def __init__(self, user, session, buffer = [], encoding = 'utf-8'):
        self.user = user
        self.session = session
        self.buffer = buffer
        self.blank_line = 0
        self.encoding = encoding
        self.globals = {}
        self.locals = {}
    
    def send(self, statement):
        """
        sends statements and gets the result of execution
        or evaluation of the statement in response.
        
        """
        self.buffer.append(statement)
        
        if ends_with(statement, u'\n'): ## this actually checks for statement been a blank line.
            self.blank_line += 1

        if ends_with(statement, u':'):
            return u'...'.encode(self.encoding)
        elif len(self.buffer) > 1:
            if self.blank_line == 1:
                statement = ''.join(self.buffer)
                try:
                    exec(statement, self.globals, self.locals)
                    ## we should get return value (if any) to the user....
                except:
                    ## get traceback error and pass it to user
                    pass
                finally:
                    self.buffer = []
                    self.blank_line = 0
            else:
                return u'...'.encode(self.encoding)
        else:
            try:
                exec(statement, self.globals, self.locals)
            except:
                ## get traceback erro and pass it to user
                pass
            finally:    
                self.buffer = []
                self.blank_line = 0


    
