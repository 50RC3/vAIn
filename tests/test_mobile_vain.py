import unittest
from mobile_vain import MobileNode  # Test the new package name

class TestMobileVain(unittest.TestCase):
    def test_mobile_node_creation(self):
        """Test that MobileNode can be created with the new package name."""
        node = MobileNode("test_device_1")
        self.assertIsNotNull(node)
        self.assertEqual(node.device_id, "test_device_1")

if __name__ == '__main__':
    unittest.main()
