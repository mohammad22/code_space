import simple_repl as sr
import unittest

class BasicRepl(unittest.TestCase):

    def setUp(self):
        self.user = sr.repl('user', 1)
        self.user.send(u'a = 1\n')
        self.var1 = self.user.send(u'a\n')

    def test_userAssignsValuesToVars(self):    
        self.assertEqual(self.var1, '1\n>>> ')
    
    def test_userSpaceDoesNotLeakToGlob(self):
        self.user.send(u'dummy = 4\n')
        dummy = 3
        self.assertEqual(self.user.send(u'dummy\n'),  '4\n>>> ')
    
    def test_replBufersNonCompleteLines(self):
        self.assertEqual(self.user.send(u'def f():\n'), '... ')
        dummy = 3
        o = self.user.send(u'    print dummy\n')
        self.assertTrue(self.user.bufer[0] == u'def f():\n')
        self.assertTrue(self.user.bufer[1] == u'    print dummy\n')
        self.assertEqual(o, '... ')
        o = self.user.send(u'\n')
        self.assertEqual(len(self.user.bufer), 0)
        self.assertTrue(o == '>>> ')
        self.assertEqual(self.user.send(u'f()\n'), '4\n>>> ')

if __name__ == '__main__':
    unittest.main()



