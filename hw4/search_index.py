class SearchIndex:

    """
    Инвертированный индекс, где каждому слову соответствует множество id документов.
    _index нужен для быстрого поиска, берём готовые множества слов запроса.
    _doc_words нужен для remove и повторного add, чтобы не перебирать весь индекс, а сразу знать, какие слова убрать у документа.
    _doc_counts нужен для удаления вкладов документа из _counts.
    _counts нужен для top_words, чтобы не пересчитывать всё каждый раз.
    """

    def __init__(self):
        self._index = {}       # слово -> set(doc_id)
        self._doc_words = {}   # doc_id -> set(слов)
        self._doc_counts = {}  # doc_id -> {слово: сколько раз в документе}
        self._counts = {}      # слово -> сколько раз по всем документам

    def _words(self, text):
        return re.findall(r'\w+', text.lower())

    def add(self, doc_id, text):
        # повторное добавление заменяет старый текст
        if doc_id in self._doc_words:
            self.remove(doc_id)

        words = self._words(text)
        for w in set(words):
            if w in self._index:
                self._index[w].add(doc_id)
            else:
                self._index[w] = {doc_id}

        per_doc = {}
        for w in words:
            per_doc[w] = per_doc.get(w, 0) + 1
            self._counts[w] = self._counts.get(w, 0) + 1

        self._doc_words[doc_id] = set(words)
        self._doc_counts[doc_id] = per_doc

    def search_all(self, *words):
        words = [w.lower() for w in words]
        if not words:
            return set()
        result = set(self._index.get(words[0], set()))
        for w in words[1:]:
            result &= self._index.get(w, set())
            if not result:
                return set()
        return result

    def search_any(self, *words):
        result = set()
        for w in words:
            result |= self._index.get(w.lower(), set())
        return result

    def remove(self, doc_id):
        if doc_id not in self._doc_words:
            return
        for w in self._doc_words[doc_id]:
            docs = self._index.get(w)
            if docs is not None:
                docs.discard(doc_id)
                if not docs:
                    del self._index[w]
        for w, cnt in self._doc_counts[doc_id].items():
            self._counts[w] -= cnt
            if self._counts[w] == 0:
                del self._counts[w]
        del self._doc_words[doc_id]
        del self._doc_counts[doc_id]

    def top_words(self, n):
        pairs = list(self._counts.items())
        pairs.sort(key=lambda p: (-p[1], p[0]))
        return pairs[:n]


if __name__ == '__main__':
    idx = SearchIndex()
    idx.add(1, 'Python is a programming language.')
    idx.add(2, 'A dict is a hash table; a set is a hash table too!')
    idx.add(3, 'Python dict and set are fast.')
    assert idx.search_all('python') == {1, 3}
    assert idx.search_all('dict', 'set') == {2, 3}
    assert idx.search_all('python', 'hash') == set()
    assert idx.search_any('language', 'fast') == {1, 3}
    assert idx.search_all('PYTHON') == {1, 3}
    assert idx.search_all('nothing') == set()
    assert idx.top_words(2) == [('a', 5), ('is', 3)]
    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}

# пустой индекс
    e = SearchIndex()
    assert e.search_all('x') == set()
    assert e.top_words(5) == []

    # слово исчезает из индекса после удаления документа
    s = SearchIndex()
    s.add(1, 'alpha beta')
    s.remove(1)
    assert s.search_all('alpha') == set()

    # повторный add заменяет старый текст
    s.add(1, 'old text')
    s.add(1, 'brand new')
    assert s.search_all('old') == set()
    assert s.search_all('brand') == {1}

    print('Все проверки пройдены.')
