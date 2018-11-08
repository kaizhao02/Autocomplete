import unittest
from query_serving import QueryServer

class TestQueryServer(unittest.TestCase):
	
	def test_basic_serialization(self):
		""" Tests for basic correctness of serialization on QueryServer objects.
		"""

		query_server = QueryServer()
		query_server2 = QueryServer()

		query_server.insert("foo", 1)
		query_server.insert("bar", 2)

		encoding = query_server.serialize()

		query_server2.deserialize(encoding)

		self.assertEqual(encoding, query_server2.serialize())

	def test_basic_queries(self):
		""" Tests for basic correctness of querying words with prefixes.
		"""

		query_server = QueryServer()

		query_server.insert("foo", 1)
		query_server.insert("bar", 2)
		query_server.insert("bar_foo", 3)
		query_server.insert("foo_bar", 4)

		expected_foo = ["foo_bar", "bar_foo", "foo"]
		expected_bar = ["foo_bar", "bar_foo", "bar"]

		self.assertEqual(query_server.get_completions("foo"), expected_foo)
		self.assertEqual(query_server.get_completions("bar"), expected_bar)


def main():
	unittest.main()

if __name__ == "__main__":
	main()