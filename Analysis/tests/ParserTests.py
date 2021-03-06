import unittest
import random
from Analysis.ResAnalyser import PDF_Parser

# Pro tip - Am a noob at Testing :|

class ParserTests(unittest.TestCase):
    """
    All tests for PDFParser class & all it's methods go here
    """
    def setUp(self):
        self.parser = PDF_Parser(testing=True)

    def test_is_credit(self):
        self.assertEqual(6, self.parser.is_credit('6'))
        self.assertEqual(8, self.parser.is_credit('8'))
        self.assertEqual(10, self.parser.is_credit('0'))
        self.assertEqual(False, self.parser.is_credit('7.4'))
        self.assertEqual(False, self.parser.is_credit('AA'))

    def test_is_gpa(self):
        pass

    def test_getdata(self):
        pass

    def test_get_stud_type(self):
        pass

    def test_get_batch(self):
        pass

if __name__ == '__main__':
    unittest.main()
