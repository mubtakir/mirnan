import sys
from src.physics.morpho_phasic import MorphoPhasicEngine
from src.physics.generator import UniversalRootExtractor

extractor = UniversalRootExtractor()
engine = MorphoPhasicEngine()

test_words = [
    'استغاث', 'مستشفى', 'تكنولوجيا', 'أشياء', 'ملائكة', 'ميزان', 'اتساق', 'اضطراب', 'ازدهار', 'يئس',
    'thought', 'caught', 'went', 'been', 'done', 'saw', 'polymorphism', 'asynchronous', 'encapsulation', 'instantiation'
]

with open("test_output_hard.txt", "w", encoding="utf-8") as f:
    f.write("Testing hard words root extraction:\n")
    for w in test_words:
        root, confidence = extractor.extract(w)
        pv = engine.compute_morph_phase(w)
        has_pv = pv is not None
        f.write(f"Word: {w:15} -> Root: {str(root):10} (Conf: {confidence:.2f}) | PV Created: {has_pv}\n")
