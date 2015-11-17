import simple_repl as sr
import unittest

class BasicRepl(unittest.TestCase):

    def setUp(self):
        self.user = sr.repl('user', 1)
        self.user.send(u'\n')
        self.user2 = sr.repl('user2', 1)
        self.user2.send(u'\n')

    def test_userAssignsValuesToVars(self):    
        self.user.send(u'a = 1\n')
        o = self.user.send(u'a\n')
        self.assertEqual(o, '1\n>>> ', "User variable did not allocate properly in her own space.")
        self.user.send(u'\n')
    
    def test_userSpaceDoesNotLeakToGlob(self):
        self.user.send(u'dummy = 4\n')
        dummy = 3
        self.assertEqual(self.user.send(u'dummy\n'),  '4\n>>> ', "User variables leaked to the execution environment or did not allocate properly.")
        self.user.send(u'\n')
    
    def test_replBufersNonCompleteLines(self):
        self.user.send(u'dummy = 4\n')
        self.assertEqual(self.user.send(u'def f():\n'), '... ')
        dummy = 3
        o = self.user.send(u'    print dummy\n')
        self.assertTrue(self.user.bufer[0] == u'def f():\n', "Function defition is not buffered properly")
        self.assertTrue(self.user.bufer[1] == u'    print dummy\n', "Function defition is not buffered properly")
        self.assertEqual(o, '... ', "Repl is not yet waiting for the last new-line to finish fnction defition")
        o = self.user.send(u'\n')
        self.assertEqual(len(self.user.bufer), 0, "Buffer did not flush properly")
        self.assertTrue(o == '>>> ', "After finishing function-defition repl did not fall back to its normal mode")
        self.assertEqual(self.user.send(u'f()\n'), '4\n>>> ', "Function-calls does not work properly ")

    def test_usersDoesNotShareSpace(self):
        
        self.user.send(u'aa = "hi from user"\n')
        self.user2.send(u'bb = "hi from user2"\n')
        res = self.user.send(u'bb\n')
        num = res.find("NameError")
        res2 = self.user.send(u'aa\n')
        num2 = res.find("NameError")
        self.assertTrue(num != -1, "Varibales leaked from different user spaces")
        self.assertTrue(num2 != -1, "Varibales leaked from different user spaces")
        self.user.send(u'\n')
        self.user2.send(u'\n')

if __name__ == '__main__':
        unittest.main()



