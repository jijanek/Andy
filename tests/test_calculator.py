"""Test arithmetic results and division by zero using unittest."""

import unittest

from calculator import add, divide, multiply, subtract


class CalculatorTests(unittest.TestCase):
    def test_add_integers(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_negative_and_zero(self):
        self.assertEqual(add(-4, 2), -2)
        self.assertEqual(add(0, -4), -4)

    def test_add_floats(self):
        self.assertAlmostEqual(add(0.1, 0.2), 0.3)
        self.assertAlmostEqual(add(2, 0.5), 2.5)

    def test_subtract_integers(self):
        self.assertEqual(subtract(7, 2), 5)

    def test_subtract_negative_and_zero(self):
        self.assertEqual(subtract(2, 7), -5)
        self.assertEqual(subtract(2, -3), 5)
        self.assertEqual(subtract(0, 4), -4)

    def test_subtract_floats(self):
        self.assertAlmostEqual(subtract(0.3, 0.1), 0.2)
        self.assertAlmostEqual(subtract(2, 0.5), 1.5)

    def test_multiply_integers(self):
        self.assertEqual(multiply(3, 4), 12)

    def test_multiply_negative_and_zero(self):
        self.assertEqual(multiply(-3, 4), -12)
        self.assertEqual(multiply(-3, -4), 12)
        self.assertEqual(multiply(5, 0), 0)

    def test_multiply_floats(self):
        self.assertAlmostEqual(multiply(0.1, 0.2), 0.02)
        self.assertAlmostEqual(multiply(3, 0.5), 1.5)

    def test_divide_integers(self):
        self.assertEqual(divide(8, 2), 4.0)
        self.assertEqual(divide(7, 2), 3.5)

    def test_divide_negative_and_zero_numerator(self):
        self.assertEqual(divide(6, -2), -3.0)
        self.assertEqual(divide(-6, -2), 3.0)
        self.assertEqual(divide(0, 5), 0.0)

    def test_divide_floats(self):
        self.assertAlmostEqual(divide(0.3, 0.1), 3.0)
        self.assertAlmostEqual(divide(3, 0.5), 6.0)

    def test_divide_by_integer_zero(self):
        with self.assertRaises(ZeroDivisionError):
            divide(1, 0)

    def test_divide_by_float_zero(self):
        for divisor in (0.0, -0.0):
            with self.subTest(divisor=repr(divisor)):
                with self.assertRaises(ZeroDivisionError):
                    divide(1, divisor)


if __name__ == "__main__":
    unittest.main()
