import sys
import io
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.physics.word_physics import compute_word_phase_vector
from src.semantics.mafahem_parser import load_mafahem, get_concept

d = load_mafahem()
print('Mafahem count:', len(d))

sym = '🌸'
concept = get_concept(sym)
print(f"'{sym}' mapped to: '{concept}'")

v1 = compute_word_phase_vector(sym)
v2 = compute_word_phase_vector(concept)
print('Vectors match:', np.allclose(v1, v2))
