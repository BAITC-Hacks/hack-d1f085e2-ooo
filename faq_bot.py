#!/usr/bin/env python3
import re
from pathlib import Path




FAQ_PATH = Path(__file__).parent / "faq.txt"
EXIT_WORDS = {"выход", "exit", "quit", "q"}


def tokenize(text):
    # Words of 3+ chars only, to skip short prepositions/conjunctions
    # (в, и, на, по, до, ...) that would otherwise cause false matches.
    return set(re.findall(r"[а-яёa-z0-9]{3,}", text.lower()))


def load_faq(path):
    text = path.read_text(encoding="utf-8")
    entries = []
    for block in text.strip().split("\n\n"):
        question = keywords = ""
        answer_lines = []
        in_answer = False
        for line in block.strip("\n").splitlines():
            if line.startswith("Q:"):
                question = line[2:].strip()
                in_answer = False
            elif line.startswith("K:"):
                keywords = line[2:].strip()
                in_answer = False
            elif line.startswith("A:"):
                answer_lines.append(line[2:].strip())
                in_answer = True
            elif in_answer and line.strip():
                answer_lines.append(line.strip())
        if question and answer_lines:
            entries.append({
                "question": question,
                "answer": " ".join(answer_lines),
                # Only the curated K: list is used for matching; the Q: text
                # is just documentation and often contains generic words
                # ("как", "какие", ...) that would cause false matches.
                "keywords": tokenize(keywords),
            })
    return entries


def best_match(user_text, entries):
    user_tokens = tokenize(user_text)
    if not user_tokens:
        return None, 0
    best_entry, best_score = None, 0
    for entry in entries:
        score = len(user_tokens & entry["keywords"])
        if score > best_score:
            best_entry, best_score = entry, score
    return best_entry, best_score


def main():
    entries = load_faq(FAQ_PATH)
    print("FAQ-бот. Задайте вопрос про репетицию (время, команда, трек, сдача, призы).")
    print("Для выхода наберите 'выход' или 'exit'.\n")
    while True:
        try:
            user_input = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nБот: Пока!")
            break
        if not user_input:
            continue
        if user_input.lower() in EXIT_WORDS:
            print("Бот: Пока!")
            break
        entry, score = best_match(user_input, entries)
        if entry is None or score == 0:
            print("Бот: Не знаю ответа на этот вопрос. Попробуйте спросить про время, команду, трек, сдачу или призы.")
        else:
            print(f"Бот: {entry['answer']}")


if __name__ == "__main__":
    main()
