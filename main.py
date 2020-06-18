import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from TestServer import TestServer


def clear_text(element):
    """Remove all text from an element. `.clear` is broken in Chrome."""
    length = len(element.get_attribute('value'))
    element.send_keys(length * Keys.BACKSPACE)

class CrosswordTests(unittest.TestCase):
    """Tests for crossword app"""
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()

    def setUp(self):
        super(CrosswordTests, self).setUp()
        self.driver.get('http://localhost:8080/')
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'app')))
        self._disable_save_warning()
        self._set_up_test_server()
        self._set_size_to_3x3()

    def _set_up_test_server(self):
        self.driver.execute_script('window.replaceServer("//localhost:8079")')

    def _disable_save_warning(self):
        self.driver.execute_script('window.disableSaveWarning()')

    def _set_size_to_3x3(self):
        width = self.driver.find_element_by_id('width')
        clear_text(width)
        width.send_keys('3')
        height = self.driver.find_element_by_id('height')
        clear_text(height)
        height.send_keys('3')

    def _get_focused_element(self):
        # Rename this so it's easier to understand.
        return self.driver.switch_to.active_element

    def test_set_size(self):
        """Make sure that the grid resizes properly."""
        # We call _set_size_to_3x3 in our setup.
        # A 3x3 grid should have 9 cells
        cells = self.driver.find_elements_by_class_name('cell')
        self.assertEqual(len(cells), 9)

        # Without any dark squares, we should have 3 across and 3 down clues
        clues = self.driver.find_elements_by_class_name('clue')
        self.assertEqual(len(clues), 6)


    def test_get_word_completions(self):
        """Test that we can get word completions from the test server"""
        first_cell = self.driver.find_element_by_id('0,0')
        first_cell.click()
        first_cell.send_keys(Keys.RETURN)

        # The exploreword should be set to the value of the current word.
        # We have set the size to 3x3 in our setup.
        exploreword = self.driver.find_element_by_id('exploreword')
        self.assertEqual(exploreword.get_attribute('value'), '...')

        # Wait for the words to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'word')))

        # Make sure that our test words have loaded.
        words = self.driver.find_elements_by_class_name('word')
        self.assertEqual(len(words), 10)
        self.assertEqual(words[0].get_attribute('value'), 'AAA')
        self.assertEqual(words[9].get_attribute('value'), 'JJJ')

    def test_tab_switching(self):
        """Test that switching from element to element using tab works."""

        # Hitting tab from the crossword should take us to the current clue.
        # In a 3x3, the center cell will be part of 4 across.
        center_cell = self.driver.find_element_by_id('1,1')
        center_cell.click()
        center_cell.send_keys(Keys.TAB)

        # 0,1,1 = 4 across
        center_cell_across_clue = self.driver.find_element_by_id('0,1,1')

        self.assertEqual(self._get_focused_element(), center_cell_across_clue)

        # Hitting tab from the clue should take us to the explore word
        center_cell_across_clue.send_keys(Keys.TAB)
        exploreword = self.driver.find_element_by_id('exploreword')
        self.assertEqual(self._get_focused_element(), exploreword)

        # Hitting tab from the explore word should take us to the wordlist.
        exploreword.send_keys(Keys.TAB)
        wordlist = self.driver.find_element_by_id('wordlist')
        self.assertEqual(self._get_focused_element(), wordlist)

        # Hitting tab from the wordlist should take us to the desired wordlist
        wordlist.send_keys(Keys.TAB)
        desired_words = self.driver.find_element_by_id('desiredwords')
        self.assertEqual(self._get_focused_element(), desired_words)

        # Hitting shift+tab from the desired wordlist should take us back to the wordlist.
        desired_words.send_keys(Keys.SHIFT + Keys.TAB)
        self.assertEqual(self._get_focused_element(), wordlist)

        # Hitting shift+tab from the wordlist should take us back to the exploreword.
        wordlist.send_keys(Keys.SHIFT + Keys.TAB)
        self.assertEqual(self._get_focused_element(), exploreword)

        # Hitting shift+tab from the exploreword should take us back to the clue.
        exploreword.send_keys(Keys.SHIFT + Keys.TAB)
        self.assertEqual(self._get_focused_element(), center_cell_across_clue)

        # Hitting shift+tab from the clue should take us back to the center cell.
        center_cell_across_clue.send_keys(Keys.SHIFT + Keys.TAB)
        self.assertEqual(self._get_focused_element(), center_cell)

    def test_get_completions(self):
        """Test that getting completions incl. local words works."""
        desired_words = self.driver.find_element_by_id("desiredwords")
        desired_words.send_keys("""
            haa
            hbb
            hcc
            hdd
            hee
            hff
            hgg
            hhh
            hii
            hjj
            hkk
            hll
        """.replace(' ', ''))

        first_cell = self.driver.find_element_by_id('0,0')
        first_cell.send_keys('H')
        first_cell.send_keys(Keys.RETURN)

        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, 'wordlist__page'), "(Page 1)"))

        wordlist = self.driver.find_element_by_id('wordlist')
        options = [x.get_attribute('value') for x in wordlist.find_elements_by_tag_name('option')]
        self.assertEqual(options, [
            "HAA", "HBB", "HCC", "HDD", "HEE", "HFF", "HGG", "HHH", "HII", "HJJ"
        ])

        wordlist.send_keys(Keys.ARROW_RIGHT)
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, 'wordlist__page'), "(Page 2)"))
        options = [x.get_attribute('value') for x in wordlist.find_elements_by_tag_name('option')]
        self.assertEqual(options, [
            "HKK", "HLL", "HMM", "HNN"
        ])

        wordlist.send_keys(Keys.ARROW_LEFT)
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, 'wordlist__page'), "(Page 1)"))
        options = [x.get_attribute('value') for x in wordlist.find_elements_by_tag_name('option')]
        self.assertEqual(options, [
            "HAA", "HBB", "HCC", "HDD", "HEE", "HFF", "HGG", "HHH", "HII", "HJJ"
        ])

        wordlist.send_keys(Keys.ARROW_RIGHT)
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, 'wordlist__page'), "(Page 2)"))
        options = [x.get_attribute('value') for x in wordlist.find_elements_by_tag_name('option')]
        self.assertEqual(options, [
            "HKK", "HLL", "HMM", "HNN"
        ])


if __name__ == '__main__':
    test_server = TestServer()
    test_server.run()
    unittest.main()
    test_server.terminate()
