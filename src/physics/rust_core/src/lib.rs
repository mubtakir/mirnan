use pyo3::prelude::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2, IntoPyArray};
use rayon::prelude::*;
use pyo3::wrap_pyfunction;

/// يحسب التوافق الجيبي (Cosine Similarity) بين متجه الكلمة ومصفوفة من متجهات السياق
/// يستخدم التسريع الموازي عبر Rayon.
#[pyfunction]
fn compute_resonance_batch<'py>(
    py: Python<'py>,
    word_pv: PyReadonlyArray1<f64>,
    context_pvs: PyReadonlyArray2<f64>,
    beta: f64,
) -> PyResult<&'py numpy::PyArray1<f64>> {
    let word_slice = word_pv.as_slice()?;
    let context_view = context_pvs.as_array();
    
    let rows = context_view.nrows();
    
    // حساب موازي للتوافق بين متجه الكلمة وكل متجه سياق
    let mut activations = vec![0.0; rows];
    
    activations.par_iter_mut().enumerate().for_each(|(i, act)| {
        let ctx_row = context_view.row(i);
        let mut dot = 0.0;
        let mut norm_w = 0.0;
        let mut norm_c = 0.0;
        
        // حساب الجداء النقطي والمعايير
        for j in 0..word_slice.len() {
            let w = word_slice[j];
            let c = ctx_row[j];
            dot += w * c;
            norm_w += w * w;
            norm_c += c * c;
        }
        
        let norm = (norm_w * norm_c).sqrt();
        let cos_sim = if norm > 1e-10 { dot / norm } else { 0.0 };
        
        // تطبيق قوة الرنين (beta) كدالة أسية
        *act = (beta * cos_sim).exp();
    });
    
    Ok(activations.into_pyarray(py))
}

#[pymodule]
fn mirnan_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_resonance_batch, m)?)?;
    Ok(())
}
