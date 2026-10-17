"""Unit tests of the estimators, run on the functions as defined in the notebook."""
import numpy as np
import pytest


def ar2(a1, a2, n=100_000, seed=0):
    rng = np.random.default_rng(seed); e = rng.normal(0, 1, n); y = np.zeros(n)
    for t in range(2, n):
        y[t] = a1 * y[t - 1] + a2 * y[t - 2] + e[t]
    y = y[1000:]
    return y, 1 - 1.0 / y.var()


@pytest.mark.parametrize("a1,a2", [(0.6, 0.2), (0.9, -0.3), (0.3, 0.0)])
def test_linear_ceiling_recovers_analytic_ar2(nb, a1, a2):
    """Paper Sec 1.2 / 2.4 / 2.7: estimator within 0.003 of the closed-form R^2."""
    y, true_r2 = ar2(a1, a2)
    assert abs(nb["ceiling_linear"](y) - true_r2) < 0.003


def test_linear_ceiling_white_noise_is_near_zero(nb):
    y = np.random.default_rng(1).normal(size=5000)
    assert 0 <= nb["ceiling_linear"](y) < 0.01


def test_linear_ceiling_in_unit_interval(nb):
    t = np.arange(504)
    y = 0.5 + 0.3 * np.sin(2 * np.pi * t / 12) + 0.05 * np.random.default_rng(2).normal(size=504)
    assert 0 <= nb["ceiling_linear"](y) <= 1


def test_deseason_removes_two_harmonics(nb):
    t = np.arange(504)
    y = 1 + np.sin(2 * np.pi * t / 12) + 0.5 * np.cos(4 * np.pi * t / 12)
    assert np.abs(nb["deseason"](y)).max() < 1e-10


def test_ksg_close_to_gaussian_analytic(nb):
    rng = np.random.default_rng(3); z = rng.normal(size=800); x = z + 0.5 * rng.normal(size=800)
    rho = 1 / np.sqrt(1.25); true = -0.5 * np.log(1 - rho ** 2)
    assert abs(nb["ksg_mi"](x[:, None], z) - true) < 0.1


def test_ksg_finite_on_floor_tied_series(nb):
    """Paper Sec 2.4: hyper-arid floor ties must not send MI to infinity; capped at 5 nats."""
    rng = np.random.default_rng(4)
    y = np.where(rng.random(504) < 0.8, 0.04, 0.04 + rng.random(504) * 0.1)
    X, Y = nb["lagmat"](y, [1, 2, 12])
    mi = nb["ksg_mi"](X, Y)
    assert np.isfinite(mi) and 0 <= mi <= 5


def test_sampen_regular_below_noise(nb):
    t = np.arange(400)
    reg = np.sin(2 * np.pi * t / 12)
    noise = np.random.default_rng(5).normal(size=400)
    assert nb["sampen"](reg) < nb["sampen"](noise)


def test_nse_reference_points(nb):
    o = np.random.default_rng(6).normal(size=60)
    assert nb["nse"](o, o) == pytest.approx(1.0)
    assert nb["nse"](o, np.full_like(o, o.mean())) == pytest.approx(0.0)


def test_design_matrix_alignment(nb):
    y = np.arange(30.0); months = np.arange(30)
    X, Y, M = nb["design"](y, months)
    assert X.shape == (18, 12) and np.all(X[:, 0] == Y - 1) and np.all(X[:, 11] == Y - 12)


def test_esn_does_not_diverge(nb):
    """Paper Sec 2.5: standardised inputs + inner-holdout ridge; an earlier fixed ridge diverged."""
    y, _ = ar2(0.8, 0.0, n=2500, seed=7)          # 1500 points after the 1000-step burn-in
    X, Y, _ = nb["design"](y, np.arange(len(y)))
    p = nb["ESN"](seed=0).fit(X[:1000], Y[:1000]).predict(X[1000:])
    assert nb["nse"](Y[1000:], p) > 0.4
