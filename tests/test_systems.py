import unittest
from CLI.src.systems import guess_os

class TestGuessOs(unittest.TestCase):

    def test_windows(self):
        self.assertEqual(guess_os([135, 445]), 'Windows')

    def test_linux(self):
        self.assertEqual(guess_os([22, 80]), 'Linux/Unix')

    def test_unknown(self):
        self.assertEqual(guess_os([8080]), 'Desconocido')

    def test_majority_wins(self):
        self.assertEqual(guess_os([22, 135, 445]), 'Windows')
if __name__ == '__main__':
    unittest.main()
