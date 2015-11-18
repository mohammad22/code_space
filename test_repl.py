import simple_repl as sr
import unittest
import os
from tempfile import NamedTemporaryFile 

class BasicRepl(unittest.TestCase):

    def setUp(self):
        self.user = sr.repl('user', 1)
        self.user.send(u'\n')
        self.user2 = sr.repl('user2', 1)
        self.user2.send(u'\n')
    
    def tearDown(self):
        del self.user
        del self.user2

    def test_userAssignsValuesToVars(self):    
        self.user.send(u'a = 1\n')
        o = self.user.send(u'a\n')
        self.assertEqual(o, '1\n>>> ', "User variable did not allocate properly in her own space.")
    
    def test_importWorkInAlignment(self):
        self.user.send(u'import os\n')
        self.user.send(u'dummy = 4\n')
        self.assertTrue('os' in self.user.glob, "import did not work properly")
        o = self.user.send(u'dummy\n')
        self.assertEqual(o, '4\n>>> ', "defining variables did not work after import statement")

    def test_userSpaceDoesNotLeakToGlob(self):
        self.user.send(u'dummy = 4\n')
        dummy = 3
        self.assertEqual(self.user.send(u'dummy\n'),  '4\n>>> ', "User variables leaked to the execution environment or did not allocate properly.")
    
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

    def test_userTempFilesAreDifferent(self):
        self.assertTrue(self.user.fille != self.user2.fille, "Diffeent users has got the same Temp-files")

    def test_tempDestroyedByUserDeletion(self):
        self.user3 = sr.repl('user3', 1)
        f = self.user3.fille
        del self.user3
        self.assertFalse(os.path.exists(f), "Temp-file is not destructed properly after deleting user ")

    def test_codepathFillsGlob(self):
        file = NamedTemporaryFile(mode = 'w+t', suffix = ".py", delete = False)
        file.write("name_1 = 'hi'")
        file.write("\n")
        file.close()
        self.user4 = sr.repl('user4', 1, codepath = file.name)
        self.assertTrue(self.user4.send(u'name_1\n') == 'hi\n>>> ', "codepath is not properly popultaed in the users global namespace")
        del self.user4
        os.remove(file.name)

    def test_nonexistingcodepathRaisesIOError(self):
        self.assertRaises(IOError, sr.repl, 'user5', 1, codepath = "not_exists.py")
        
       
    def test_nonpythonFilesRaiseIOError(self):
        file = NamedTemporaryFile(mode = 'w+t', suffix = ".ppy", delete = False)
        file.write("name_1 = 'hi'")
        file.write("\n")
        file.close()
        self.assertRaises(IOError, sr.repl, 'user6', 1, codepath = file.name)  
        os.remove(file.name)



if __name__ == '__main__':
        unittest.main()



