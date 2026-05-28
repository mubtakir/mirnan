import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from src.physics.synchronize import synchronize
from src.physics.generator import Generator

with open('data/corpus.txt', encoding='utf-8') as f:
    c1 = f.read()
with open('data/dialogue_corpus.txt', encoding='utf-8') as f:
    c2 = f.read()
corpus_list = [c1, c2]

vocab, K, syntax = synchronize(corpus_list, window=5)
gen = Generator(vocab, K, beam_width=3, top_k=250, syntax_field=syntax, beta=2.0)

prompt = "ما مجموع 1 + 2"
print("Tokens:", [vocab.id2word.get(vocab.get(w)) for w in prompt.split() if vocab.get(w) is not None])
print("Standard:", gen.generate(prompt, max_words=10, mode='standard'))
print("Quantum:", gen.generate(prompt, max_words=10, mode='quantum'))
