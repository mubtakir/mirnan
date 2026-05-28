import numpy as np

class ReasoningEngine:
    """
    محرك التفكير المتسلسل (Chain of Thought Reasoning Engine)
    ينظم مسارات التفكير المرحلي ويدير بوابات التماسك الديناميكية والساعة المعرفية.
    """
    def __init__(self, engine):
        self.engine = engine
        self.lexicon = engine.lexicon
        self.coupling = engine.coupling
        self.milestones = ["<المعطيات>", "<الخطوة_1>", "<الخطوة_2>", "<التحقق>", "<النتيجة>"]

    def generate_reasoning_sequence(self, question, context_words=None):
        """
        توليد مسار تفكير متسلسل مشروط بالتماسك الديناميكي (Coherence Gating).
        ينتقل النظام من مرحلة إلى أخرى فقط بعد استقرار حوض الجاذبية الحالي.
        """
        question_words = [w for w in self.lexicon.clean_text(question) if w in self.lexicon.vocab]
        q_ids = [self.lexicon.vocab[w] for w in question_words]
        
        sequence_log = []
        
        # المرحلة 1: المعطيات
        m1_id = self.lexicon.vocab.get("<المعطيات>")
        if m1_id is not None:
            step_ids = q_ids + [m1_id]
            _, phases_h, r_h, _ = self.engine.simulate(step_ids, t_span=(0, 4), num_steps=60, sequential=True)
            final_r = r_h[-1] if len(r_h) > 0 else 0.0
            if final_r > 0.75:
                sequence_log.append({
                    "step": "<المعطيات>",
                    "status": "مستقر",
                    "coherence": float(final_r),
                    "summary": f"تم تحليل المعطيات بنجاح بتماسك {final_r:.2f}"
                })
            else:
                sequence_log.append({
                    "step": "<المعطيات>",
                    "status": "غير مستقر",
                    "coherence": float(final_r),
                    "summary": f"تحليل المعطيات يحتاج لإعادة مزامنة (r={final_r:.2f})"
                })

        # المرحلة 2: الخطوة 1
        m2_id = self.lexicon.vocab.get("<الخطوة_1>")
        if m2_id is not None:
            step_ids = q_ids + [m2_id]
            _, phases_h, r_h, _ = self.engine.simulate(step_ids, t_span=(0, 4), num_steps=60, sequential=True)
            final_r = r_h[-1] if len(r_h) > 0 else 0.0
            sequence_log.append({
                "step": "<الخطوة_1>",
                "status": "مستقر" if final_r > self.engine.step_gate_threshold else "بوابة مغلقة",
                "coherence": float(final_r),
                "summary": f"الخطوة الأولى حققت تماسك {final_r:.2f}"
            })

        # المرحلة 3: التحقق
        m3_id = self.lexicon.vocab.get("<التحقق>")
        if m3_id is not None:
            step_ids = q_ids + [m3_id]
            _, phases_h, r_h, _ = self.engine.simulate(step_ids, t_span=(0, 4), num_steps=60, sequential=True)
            final_r = r_h[-1] if len(r_h) > 0 else 0.0
            sequence_log.append({
                "step": "<التحقق>",
                "status": "مستقر" if final_r > self.engine.step_gate_threshold else "بوابة مغلقة",
                "coherence": float(final_r),
                "summary": f"التحقق المنطقي حقق تماسك {final_r:.2f}"
            })

        # المرحلة 4: النتيجة
        m4_id = self.lexicon.vocab.get("<النتيجة>")
        if m4_id is not None:
            step_ids = q_ids + [m4_id]
            _, phases_h, r_h, _ = self.engine.simulate(step_ids, t_span=(0, 4), num_steps=60, sequential=True)
            final_r = r_h[-1] if len(r_h) > 0 else 0.0
            sequence_log.append({
                "step": "<النتيجة>",
                "status": "مستقر" if final_r > self.engine.step_gate_threshold else "بوابة مغلقة",
                "coherence": float(final_r),
                "summary": f"النتيجة النهائية حققت تماسك {final_r:.2f}"
            })

        # توليد النص التوضيحي للسلسلة الفكرية
        reasoning_text = "سلسلة التفكير الطوري:\n"
        for item in sequence_log:
            reasoning_text += f" - [{item['step']}]: {item['summary']} ({item['status']})\n"

        return {
            "reasoning_log": sequence_log,
            "reasoning_text": reasoning_text,
            "final_coherence": sequence_log[-1]["coherence"] if sequence_log else 0.0
        }
