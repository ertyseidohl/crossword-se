"""Tests for Crossword-fe."""
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def clear_text(element):
    length = len(element.get_attribute('value'))
    element.send_keys(length * Keys.BACKSPACE)

class CrosswordTests(unittest.TestCase):
    """Tests for crossword app"""
    def setUp(self):
        super(CrosswordTests, self).setUp()
        self.driver = webdriver.Chrome()
        self.driver.get('http://localhost:8081/')
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "app")))

    def tearDown(self):
        self.driver.close()

    def test_set_size(self):
        """Test the width and height inputs work"""
        width = self.driver.find_element_by_id('width')
        clear_text(width)
        width.send_keys('3')
        height = self.driver.find_element_by_id('height')
        clear_text(height)
        height.send_keys('3')
        cells = self.driver.find_elements_by_class_name('cell')
        assert len(cells) == 9

if __name__ == '__main__':
    unittest.main()
