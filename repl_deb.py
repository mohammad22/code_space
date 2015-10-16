import simple_repl as sr

def main():
    mo = sr.repl('mo', 1)
    mo.send(u'a = 1\n')
    mo.send(u'a\n')
    mo.send(u'def f():\n')
    mo.send(u'print a\n')
    mo.send(u'\n')
    mo.send(u'a\n')



if __name__ == '__main__':
    main()



