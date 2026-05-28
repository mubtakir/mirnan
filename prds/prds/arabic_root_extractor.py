import os
import json
from typing import Dict, List, Optional, Tuple


class ArabicRootExtractor:
    def __init__(self, semantic_db_path: Optional[str] = None):
        self.augmentation_letters = set("سألتمونيها")
        self.definite_article = "ال"
        self.attached_pronouns = [
            "هم", "هن", "هما", "ها", "ه",
            "كم", "كن", "كما", "ك",
            "نا", "ني", "ي"
        ]
        self.prefixes = ["و", "ف", "ب", "ل", "ك", "س"]
        self.known_roots = {}
        self.word_to_root_cache = {}
        if semantic_db_path and os.path.exists(semantic_db_path):
            self._load_semantic_db(semantic_db_path)

    def _load_semantic_db(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            roots = data.get("roots", {})
            for root_key, root_data in roots.items():
                root = root_data.get("root", root_key)
                self.known_roots[root_key] = root
                derivatives = root_data.get("derivatives", [])
                for deriv in derivatives:
                    self.word_to_root_cache[deriv] = root_key
        except Exception:
            pass

    def extract(self, word: str) -> Tuple[str, float]:
        if word in self.word_to_root_cache:
            return self.word_to_root_cache[word], 1.0
        clean_word = self._clean_word(word)
        if clean_word in self.word_to_root_cache:
            return self.word_to_root_cache[clean_word], 0.9
        root, confidence = self._extract_root_manual(clean_word)
        self.word_to_root_cache[word] = root
        return root, confidence

    def _clean_word(self, word: str) -> str:
        word = self._remove_diacritics(word)
        if word.startswith(self.definite_article):
            word = word[2:]
        for prefix in self.prefixes:
            if word.startswith(prefix) and len(word) > 3:
                word = word[1:]
                break
        for pronoun in sorted(self.attached_pronouns, key=len, reverse=True):
            if word.endswith(pronoun) and len(word) > len(pronoun) + 2:
                word = word[:-len(pronoun)]
                break
        return word

    @staticmethod
    def _remove_diacritics(text: str) -> str:
        diacritics = "ًٌٍَُِّْـ"
        return ''.join(c for c in text if c not in diacritics)

    def _extract_root_manual(self, word: str) -> Tuple[str, float]:
        if len(word) < 2:
            return word, 0.1
        root_letters = []
        for i, char in enumerate(word):
            if i == 0:
                root_letters.append(char)
            elif char not in self.augmentation_letters:
                root_letters.append(char)
            elif len(root_letters) < 3:
                root_letters.append(char)
        if len(root_letters) >= 3:
            root = "-".join(root_letters[:3])
            confidence = 0.7 if len(root_letters) == 3 else 0.5
        elif len(root_letters) == 2:
            root = "-".join(root_letters)
            confidence = 0.4
        else:
            root = root_letters[0] if root_letters else word[0]
            confidence = 0.2
        return root, confidence

    def batch_extract(self, words: List[str]) -> List[Tuple[str, float]]:
        return [self.extract(word) for word in words]
