#!/usr/bin/python

import os
import sys
from contextlib import contextmanager
import traceback


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
                if command.startswith(u'print'):
                    exec(command, glob, None)
                else:
                    exec(u''.join([u'print ', command]), glob)
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



