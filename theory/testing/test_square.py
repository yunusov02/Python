import unittest
from square import Square

class TestSquare(unittest.TestCase):
    def test_area(self):
        square = Square(10)
        area = square.area()
        self.assertEqual(area, 100)

    def test_length_with_wrong_type(self):
        with self.assertRaises(TypeError):
            square = Square("10")
    
    def test_length_with_zero_and_negative(self):
        with self.assertRaises(ValueError):
            square = Square(0)
            square = Square(-1)


if __name__ == "__main__":
    unittest.main()
