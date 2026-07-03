import unittest

class TestInventorySystem(unittest.TestCase):
    
    def test_sample_pass(self):
        """A simple dummy test that should pass"""
        self.assertEqual(1, 1)

    def test_sample_payload(self):
        """Another basic dictionary schema check"""
        sample_item = {"product_name": "Almond Milk"}
        self.assertIn("product_name", sample_item)

if __name__ == '__main__':
    unittest.main()