use ndarray::Array2;
use num_complex::Complex64;
use pyo3::prelude::*;
use rustfft::FftPlanner;
use std::sync::Mutex;

/// Compute word spectrum FFT: given a (n, 22) matrix of letter phase vectors,
/// returns (frequencies, amplitudes, phases) for top 6 components.
#[pyfunction]
fn word_spectrum_fft(letter_vecs: Vec<Vec<f64>>) -> PyResult<(Vec<f64>, Vec<f64>, Vec<f64>)> {
    let n = letter_vecs.len();
    if n == 0 {
        return Ok((vec![], vec![], vec![]));
    }
    // Build (n, 22) array, pad to at least 3
    let n_eff = n.max(3);
    let d = letter_vecs[0].len();
    let mut data = Array2::<f64>::zeros((n_eff, d));
    for i in 0..n {
        for j in 0..d.min(letter_vecs[i].len()) {
            data[[i, j]] = letter_vecs[i][j];
        }
    }
    // Duplicate last row if n < 3
    if n < n_eff {
        let last = n.saturating_sub(1);
        for j in 0..d {
            let val = data[[last, j]];
            for i in n..n_eff {
                data[[i, j]] = val;
            }
        }
    }

    // Real FFT: n_fft = n_eff/2 + 1
    let n_fft = n_eff / 2 + 1;

    // Build complex input per column
    let mut planner = FftPlanner::<f64>::new();
    let fft = planner.plan_fft_forward(n_eff);

    let mut magnitudes = vec![0.0_f64; n_fft];
    let mut phases = vec![0.0_f64; n_fft];
    let mut frequencies = vec![0.0_f64; n_fft];

    for j in 0..d {
        let mut signal: Vec<Complex64> = (0..n_eff)
            .map(|i| Complex64::new(data[[i, j]], 0.0))
            .collect();
        fft.process(&mut signal);
        for k in 0..n_fft {
            let mag = signal[k].norm();
            let ph = signal[k].arg();
            magnitudes[k] += mag;
            phases[k] += ph;
        }
    }
    // Average over dimensions
    for k in 0..n_fft {
        magnitudes[k] /= d as f64;
        phases[k] /= d as f64;
        frequencies[k] = k as f64 / n_eff as f64;
    }

    // Sort by magnitude, keep top 6
    let n_comp = n_fft.min(6);
    let mut indices: Vec<usize> = (0..n_fft).collect();
    indices.sort_by(|&a, &b| {
        magnitudes[b]
            .partial_cmp(&magnitudes[a])
            .unwrap_or(std::cmp::Ordering::Equal)
    });

    let top_k = &indices[..n_comp];
    let freqs: Vec<f64> = top_k.iter().map(|&i| frequencies[i]).collect();
    let amps: Vec<f64> = top_k.iter().map(|&i| magnitudes[i]).collect();
    let phs: Vec<f64> = top_k.iter().map(|&i| phases[i]).collect();

    Ok((freqs, amps, phs))
}

/// One step of Kuramoto RK4 integration.
#[pyfunction]
fn kuramoto_step(
    theta: Vec<f64>,
    omega: Vec<f64>,
    K_matrix: Vec<Vec<f64>>,
    dt: f64,
) -> PyResult<Vec<f64>> {
    let n = theta.len();
    if n == 0 {
        return Ok(vec![]);
    }

    let k1 = compute_dtheta(&theta, &omega, &K_matrix, n);
    let mut y1: Vec<f64> = theta.iter().zip(k1.iter()).map(|(t, k)| t + 0.5 * dt * k).collect();
    let k2 = compute_dtheta(&y1, &omega, &K_matrix, n);
    let mut y2: Vec<f64> = theta.iter().zip(k2.iter()).map(|(t, k)| t + 0.5 * dt * k).collect();
    let k3 = compute_dtheta(&y2, &omega, &K_matrix, n);
    let mut y3: Vec<f64> = theta.iter().zip(k3.iter()).map(|(t, k)| t + dt * k).collect();
    let k4 = compute_dtheta(&y3, &omega, &K_matrix, n);

    let result: Vec<f64> = (0..n)
        .map(|i| {
            theta[i] + (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i])
        })
        .collect();
    Ok(result)
}

fn compute_dtheta(theta: &[f64], omega: &[f64], K: &[Vec<f64>], n: usize) -> Vec<f64> {
    let mut dtheta = vec![0.0_f64; n];
    for i in 0..n {
        dtheta[i] = omega[i];
        for j in 0..n {
            if i == j {
                continue;
            }
            let k_ij = if i < K.len() && j < K[i].len() {
                K[i][j]
            } else {
                0.0
            };
            dtheta[i] += k_ij * (theta[j] - theta[i]).sin();
        }
    }
    dtheta
}

/// Compute the Kuramoto order parameter R.
#[pyfunction]
fn kuramoto_order(theta: Vec<f64>) -> f64 {
    let n = theta.len() as f64;
    if n == 0.0 {
        return 0.0;
    }
    let (sum_re, sum_im): (f64, f64) = theta.iter().fold((0.0, 0.0), |(re, im), &t| {
        (re + t.cos(), im + t.sin())
    });
    (sum_re * sum_re + sum_im * sum_im).sqrt() / n
}

#[pymodule]
fn mirnan_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(word_spectrum_fft, m)?)?;
    m.add_function(wrap_pyfunction!(kuramoto_step, m)?)?;
    m.add_function(wrap_pyfunction!(kuramoto_order, m)?)?;
    Ok(())
}
