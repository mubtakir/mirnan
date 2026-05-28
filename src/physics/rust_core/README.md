# Mirnan Rust Accelerator

تستخدم هذه المكتبة لغة `Rust` لتسريع عمليات الجبر الخطي الكثيفة (مثل حساب التوافق الجيبي المتوازي) التي يعتمد عليها المولد الكمومي.

## التثبيت والتجميع

1. تأكد من تثبيت بيئة `Rust` و `Cargo`.
2. قم بتثبيت أداة `maturin`:
   ```bash
   pip install maturin
   ```
3. ترجم الكود وقم بتثبيته كحزمة بايثون ضمن بيئتك:
   ```bash
   maturin develop --release
   ```
4. في كود بايثون يمكنك الآن استخدام:
   ```python
   import mirnan_rust
   # mirnan_rust.compute_resonance_batch(word_pv, context_pvs, beta)
   ```
