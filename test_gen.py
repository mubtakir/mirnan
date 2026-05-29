from src.api.main import get_orch
import json

orch = get_orch()
orch.set_cascade(True, 3.0)
orch.set_dialogue(True)

result = orch.generate("تخيل مدينة", max_words=10, mode='creative')
print("RESULT:", result)

report = orch.get_report()
print("REPORT:", json.dumps(report, ensure_ascii=False))
