import unittest
from nyra import validate_source

class NyravelleSyntaxTests(unittest.TestCase):
    def test_valid_workflow(self):
        source = '''
workflow Welcome {
    input name: string
    say "Hello!"
}
'''
        result = validate_source(source)
        self.assertEqual(result["workflow"], "Welcome")
        self.assertEqual(len(result["inputs"]), 1)
        self.assertEqual(result["messages"], ["Hello!"])
        self.assertEqual(result["errors"], [])
    def test_duplicate_input(self):
        source = '''
workflow Example {
    input name: string
    input name: number
}
'''
        result = validate_source(source)
        self.assertTrue(
            any("duplicate input" in error
                for error in result["errors"])
        )
    def test_unsupported_statement(self):
        source = '''
workflow Example {
    answer = generate(question)
}
'''
        result = validate_source(source)
        self.assertTrue(
            any("unsupported statement" in error
                for error in result["errors"])
        )
    def test_missing_closing_brace(self):
        source = '''
workflow Example {
    say "Hello!"
'''
        result = validate_source(source)
        self.assertTrue(
            any("close the workflow" in error
                for error in result["errors"])
        )

if __name__ == "__main__":
    unittest.main()