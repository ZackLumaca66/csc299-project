from tasks3_cli.document import DocumentManager


def test_ranked_search_prefers_more_token_matches(tmp_path):
    # Isolate data directory
    import os
    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        dm = DocumentManager()
        dm.add("Learn Python", "Python basics and advanced concepts", ["coding", "python"])
        dm.add("Python Dataclasses", "Deep dive into dataclasses in Python", ["python", "design"])
        dm.add("Groceries List", "Milk bread eggs", ["life"])
        results = dm.search("python dataclasses")
        titles = [d.title for d in results]
        # The document with both tokens in title/text should appear first
        assert titles[0] == "Python Dataclasses"
        assert "Groceries List" not in titles  # unrelated doc excluded
    finally:
        os.chdir(old)


def test_search_fallback_substring(tmp_path):
    import os
    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        dm = DocumentManager()
        dm.add("Edge Case", "Symbols !!! ???", ["misc"])
        # Query with only stopwords / punctuation should fallback to substring
        res = dm.search("!!!")
        assert res, "Fallback substring search should return doc containing punctuation"
    finally:
        os.chdir(old)