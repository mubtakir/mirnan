import sys

path = r'C:\Users\allmy\Desktop\aaa\mirnan\src\physics\generator.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_func = '''    def get_physics_report(self, prompt, result):
        if not result: return {}
        all_words = prompt.split() + result.split()
        pvs = []; masses = []; weight_labels = []
        for w in all_words:
            pv = self._get_pv_fast(w)
            pvs.append(pv)
            from src.physics.word_physics import compute_word_mass
            masses.append(float(compute_word_mass(w)))
            wgt = self.weight_resonance.get_weight(w)
            weight_labels.append(str(wgt) if wgt else "—")
        phase_angles = []
        import numpy as np
        for i, w in enumerate(all_words):
            pv = pvs[i]
            angle = float(np.arctan2(pv[1], pv[0])) if abs(pv[0]) > 1e-10 else 0.0
            phase_angles.append(float(round(angle / (2 * np.pi) % 1.0, 4)))
        target = self._target_phase(pvs)
        alignments = []
        from src.physics.word_physics import phase_similarity
        for pv in pvs:
            align = float(phase_similarity(pv[:self.old_semantic_dim], target[:self.old_semantic_dim]))
            tag = "متوافق" if align > 0.3 else ("منحرف" if align > 0.0 else "متضاد")
            alignments.append(f"{tag}_{align:.2f}")
        morph_agg = {}
        for lbl in weight_labels:
            if lbl != "—": morph_agg[lbl] = int(morph_agg.get(lbl, 0) + 1)
        beamformer_data = None
        if hasattr(self, 'beamformer') and len(all_words) > 1:
            try:
                candidate = str(all_words[-1])
                candidate_pv = pvs[-1]
                context_words = [str(w) for w in all_words[-11:-1]]
                ctx_pvs = pvs[-11:-1]
                _, weights, focus_score = self.beamformer.beamform(candidate_pv[:22], ctx_pvs, context_words)
                beamformer_data = {"candidate": candidate, "context": context_words, "weights": [float(w) for w in weights], "focus_score": float(focus_score)}
            except Exception as e:
                pass
        return {
            "word_masses": {str(w): float(round(m, 4)) for w, m in zip(all_words, masses)},
            "phase_angles": phase_angles,
            "alignments": alignments,
            "morph_weights": morph_agg,
            "ram_size": int(self.ram.size),
            "vocab_size": int(self.V),
            "top_k": [str(w) for w in all_words],
            "beamformer": beamformer_data,
        }
'''

import re
pattern = re.compile(r'    def get_physics_report\(self, prompt, result\):.*?(?=\n    def |\Z)', re.DOTALL)
new_content = pattern.sub(new_func, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
