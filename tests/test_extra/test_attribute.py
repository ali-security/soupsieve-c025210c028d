"""Test attribute selectors."""
from .. import util
import threading
import soupsieve as sv


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def assert_bad_attribute_no_timeout(self, selector, timeout=10):
        """Assert a bad attribute fails fast with a syntax error and does not backtrack indefinitely."""

        results = []

        def compile_pattern():
            """Compile the bad selector and record the outcome."""

            try:
                sv.compile(selector)
                results.append(None)
            except Exception as e:
                results.append(e)

        # Compile under a bounded wait. `signal.alarm` (as used upstream) is not
        # available on all the platforms this library supports, so use a worker
        # thread that is simply abandoned if the pattern never comes back.
        thread = threading.Thread(target=compile_pattern)
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        self.assertFalse(thread.is_alive(), 'Compiling the pattern did not complete')
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], sv.SelectorSyntaxError)

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        self.assert_bad_attribute_no_timeout('[a="' + ('x' * 300))

    def test_bad_attribute_unclosed_single_quote(self):
        """Test bad attribute with an unclosed single quoted value fails for syntax error, not timeout error."""

        self.assert_bad_attribute_no_timeout("[a='" + ('x' * 300))

    def test_bad_attribute_unclosed_identifier(self):
        """Test bad attribute with an unquoted, unterminated value fails for syntax error, not timeout error."""

        self.assert_bad_attribute_no_timeout('[a=' + ('x' * 300))
