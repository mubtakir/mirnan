import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from src.physics.synchronize import _tokenize
print("Tokens:", _tokenize("الطبيب يعالج المريض في"))
