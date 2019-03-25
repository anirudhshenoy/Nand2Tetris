import unittest
from SymbolTable import *


class SymbolTableTest(unittest.TestCase):
    st = SymbolTable()

    def setUp(self):
        pass

    def test_a_should_add_new_variable(self):
        self.st.define('x', 'int', FIELD_CONSTANT)
        self.assertEqual(len(self.st.class_table), 1)

    def test_b_should_add_second_variable(self):
        self.st.define('y', 'boolean', STATIC_CONSTANT)
        self.assertEqual(len(self.st.class_table), 2)

    def test_c_index_value_should_increment(self):
        self.assertEqual(self.st.class_index[STATIC_CONSTANT], 1)
        self.assertEqual(self.st.class_index[FIELD_CONSTANT], 1)
        self.assertEqual(self.st.varCount(FIELD_CONSTANT), 1)

    def test_c_1_should_return_kind(self):
        self.assertEqual(self.st.kindOf('x'), FIELD_CONSTANT)
        self.assertEqual(self.st.kindOf('y'), STATIC_CONSTANT)

    def test_d_should_add_variables_to_subroutine_table(self):
        self.st.startSubroutine()
        self.st.define('pointX', 'string', ARG_CONSTANT)
        self.assertEqual(len(self.st.subroutine_table), 1)

    def test_e_should_add_second_variable_to_subroutine_table(self):
        self.st.define('pointY', 'string', VAR_CONSTANT)
        self.assertEqual(len(self.st.subroutine_table), 2)

    def test_f_index_value_should_increment_for_subroutine(self):
        self.assertEqual(self.st.subroutine_index[ARG_CONSTANT], 1)
        self.assertEqual(self.st.subroutine_index[VAR_CONSTANT], 1)

    def test_g_should_return_var_count(self):
        self.assertEqual(self.st.varCount(ARG_CONSTANT), 1)

    def test_h_should_return_kind(self):
        self.assertEqual(self.st.kindOf('pointX'), ARG_CONSTANT)
        self.assertEqual(self.st.kindOf('pointY'), VAR_CONSTANT)
        print(self.st)

if __name__ == '__main__':
    unittest.main()
