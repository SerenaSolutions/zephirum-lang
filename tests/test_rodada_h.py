# -*- coding: utf-8 -*-
"""RODADA H v2.1.0 — bateria adversarial de ALTA COMPLEXIDADE.

Cada teste pensa como o cientista hostil que vai submeter a linguagem.
Cada um e FALSIFICAVEL: remova o guarda e o teste quebra.

Ataques cobertos (o que o cientista tenta primeiro):
  H1  shots correlacionados: Hoeffding nao vale — recusa com motivo
  H2  peeking de protocolo: mudar epsilon pos-hoc invalida o veredito
  H3  ZNE com ruido exponencial/oscilante: extrapolar e vender chute — recusa
  H4  kernel concentrado pelo ruido global: PSD passa, informacao morreu
  H5  MPS truncado alem do orcamento: numero truncado nao e medida
  H6  curva de decaimento do gradiente: a assinatura do plateau (McClean)
  H7  familia de testes absurda: recusa TUDO, nunca acumula risco silencioso
  H8  borda da banda de confianca: um tick alem da margem e recusa
"""
import sys, os
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from zyql_robust import (correlation_verdict, protocol_seal, protocol_check,
                         depolarized_kernel, kernel_concentration_verdict,
                         mps_truncation_verdict)
from zyql_zne import zne_verdict
from zyql_mps import MPSSim, H1 as MH1, CZ4, CNOT4, ry as mry
from zyqml_core import gradient_variance, train_verdict
from zyql_quantum_gate import adaptive_margin_family, ZYQLQuantumGate

RNG = np.random.default_rng(2309)  # semente fixa: bateria e reproduzivel


# ---------- H1: correlacao entre shots mata Hoeffding ----------
def _markov_bits(n_bits, stay=0.85, seed=7):
    rng = np.random.default_rng(seed)
    bits, b = [], rng.integers(0, 2)
    for _ in range(n_bits):
        bits.append(int(b))
        if rng.random() > stay:
            b = 1 - b
    return bits

def test_correlated_shots_are_refused():
    """FALSIFICAVEL: remova o guarda de correlacao e o teste quebra."""
    d = correlation_verdict(_markov_bits(4000))
    assert d["decision"] == "REFUSED" and d["refusal_reason"] == "CORRELATED_SHOTS"
    # controle: ruido branco passa
    d_ok = correlation_verdict(list(RNG.integers(0, 2, 4000)))
    assert d_ok["decision"] == 1 and d_ok["mode"] == "INDEPENDENCE_PLAUSIBLE"


# ---------- H2: peeking de protocolo (epsilon pos-hoc) ----------
def test_protocol_tamper_is_refused():
    spec = {"epsilon": 0.05, "shots": 2048, "family": 1,
            "stopping_rule": "fixed", "hypotheses": ["iid shots"]}
    sealed = protocol_seal(spec)
    intact = protocol_check(sealed, spec)
    assert intact["decision"] == 1 and intact["mode"] == "PROTOCOL_INTACT"
    # o ataque: depois de VER os dados, o cientista "ajusta" epsilon
    peeked = dict(spec); peeked["epsilon"] = 0.01
    tampered = protocol_check(sealed, peeked)
    assert tampered["decision"] == "REFUSED"
    assert tampered["refusal_reason"] == "PROTOCOL_TAMPERED"


# ---------- H3: ZNE adversarial (nao-monotono e exponencial) ----------
def test_zne_refuses_exponential_collapse():
    """Ruido que colapsa exponencialmente: quadratica de Richardson nao
    sustenta; o guard leave-one-out tem que recusar o chute embalado."""
    d = zne_verdict([1, 3, 5], [0.94, 0.30, 0.05])
    assert d["decision"] == "REFUSED"
    assert d["refusal_reason"] == "EXTRAPOLATION_ILL_CONDITIONED"

def test_zne_refuses_oscillating_coherent_error():
    """Erro coerente que dobra nele mesmo: valores oscilam; recusa."""
    d = zne_verdict([1, 3, 5], [0.90, 0.10, 0.90])
    assert d["decision"] == "REFUSED"

def test_zne_sound_decay_still_mitigated():
    """Controle: decaimento depolarizante honesto continua MITIGATED."""
    vals = [0.95 * 0.97 ** g for g in (1, 3, 5)]
    d = zne_verdict([1, 3, 5], vals)
    assert d["decision"] == 1 and d["mode"] == "MITIGATED"


# ---------- H4: kernel concentrado pelo ruido global ----------
def test_kernel_concentration_refused():
    """O PSD passa no ruido severo — a recusa tem que vir do guarda de
    concentracao, porque a INFORMACAO morreu mesmo com PSD intacto."""
    from zyqml_core import kernel_matrix, kernel_is_psd
    X = [[0.1, 0.9], [0.9, 0.1], [0.4, 0.4], [0.7, 0.7]]
    K = kernel_matrix(X, 2)
    K_noise = depolarized_kernel(K, 2, p=0.99)
    assert kernel_is_psd(K_noise), "ate o ruido severo mantem PSD — o perigo e outro"
    d = kernel_concentration_verdict(K_noise, 2)
    assert d["decision"] == "REFUSED"
    assert d["refusal_reason"] == "KERNEL_CONCENTRATED"
    # controle: sem ruido, kernel informativo
    d_ok = kernel_concentration_verdict(K, 2)
    assert d_ok["decision"] == 1 and d_ok["mode"] == "KERNEL_INFORMATIVE"


# ---------- H5: MPS truncado alem do orcamento ----------
def _mps_ring(n, chi, layers=6, seed=1701):
    sim = MPSSim(n, chi=chi)
    for q in range(n):
        sim.apply_1q(MH1, q)
    rng = np.random.default_rng(seed)
    for _ in range(layers):
        for q in range(n):
            sim.apply_1q(mry(float(rng.uniform(0, 2 * np.pi))), q)
        for q in range(n - 1):
            sim.apply_2q(CZ4, q, q + 1)
    return sim

def test_mps_truncation_honesty():
    """Entrelacamento volume-law com chi=2: ERRO grande => recusa.
    GHZ com chi=4: exato dentro do orcamento => passa."""
    sim2 = _mps_ring(12, chi=2)
    sim_ref = _mps_ring(12, chi=64)
    d = mps_truncation_verdict(sim2, sim_ref, budget=0.05)
    assert d["decision"] == "REFUSED"
    assert d["refusal_reason"] == "TRUNCATION_EXCEEDS_BUDGET"
    # controle: GHZ n=12 com chi=4 e exato (bond necessario = 2)
    g4, gref = MPSSim(12, chi=4), MPSSim(12, chi=64)
    for sim in (g4, gref):
        sim.apply_1q(MH1, 0)
        for q in range(1, 12):
            sim.apply_2q(CNOT4, q - 1, q)
    d_ok = mps_truncation_verdict(g4, gref, budget=0.05)
    assert d_ok["decision"] == 1 and d_ok["relative_error"] < 1e-9


# ---------- H6: curva de decaimento do gradiente (assinatura do plateau) ----------
def test_gradient_variance_decay_curve():
    """Assinatura de McClean 2018 medida de verdade: variancia do gradiente
    DECAI com o tamanho do sistema a profundidade fixa (n=6 -> 8 -> 10, L=12).
    E o veredito ternario e CONSISTENTE com o limiar declarado em toda a
    grade — virar a comparacao do limiar quebra este teste."""
    L = 12
    means = []
    for n in (6, 8, 10):
        vs = [gradient_variance(n, L, RNG.uniform(0, 2 * np.pi, L * n))
              for _ in range(3)]
        means.append(float(np.mean(vs)))
    decays = [means[i] > means[i + 1] for i in range(len(means) - 1)]
    assert all(decays), ("variancia deve decair com o numero de qubits "
                         "(McClean 2018); curva medida: %r" % means)
    # consistencia do veredito com o limiar (guarda ternaria)
    for v in (1e-1, 1e-2, 2e-3, 1e-3, 1e-6):
        d = train_verdict(10, L, v)
        if v < 1e-3:
            assert d["decision"] == "REFUSED" and d["refusal_reason"] == "GRADIENT_VANISHED"
        else:
            assert d["decision"] == 1
    # profundidade acima do orcamento declarado: recusa com motivo proprio
    d_deep = train_verdict(10, 17, 1.0)
    assert d_deep["decision"] == "REFUSED" and d_deep["refusal_reason"] == "DEPTH_EXCEEDS_BUDGET"


# ---------- H7: familia absurda recusa TUDO, nunca acumula risco ----------
def test_absurd_family_refuses_everything():
    assert adaptive_margin_family(0.05, 256, 100000) <= 0, \
        "banda Bonferroni <= 0 para familia absurda: recusa tudo"
    gate = ZYQLQuantumGate(2, lambda x: 1)
    d = gate.run_quantum(shots=256, seed=1701, epsilon=0.05, family=100000)
    assert d["decision"] == "REFUSED" and d["refusal_reason"] == "FAMILY_EXCEEDS_SHOTS"


# ---------- H8: um tick alem da banda e recusa ----------
def test_band_boundary_is_refused():
    gate = ZYQLQuantumGate(2, lambda x: 1)
    inside = gate._trivalent(0.86, 100, margin=0.15)   # >= 1-m: decide
    assert inside["decision"] == 1
    one_tick_out = gate._trivalent(0.84, 100, margin=0.15)  # centro da banda
    assert one_tick_out["decision"] == "REFUSED"
    assert one_tick_out["refusal_reason"] == "INSIDE_NOISE_BAND"


# ---------- H9: verificador de recibos entende o formato aninhado ----------
def test_receipt_verifier_handles_nested_format(tmp_path):
    """Achado real da Rodada H: o recibo G (formato aninhado {payload, selo})
    era dado como ROMPIDO pelo verificador da casa — bug da FERRAMENTA, nao
    do recibo. FALSIFICAVEL: reverta o patch e este teste quebra."""
    import json, hashlib, importlib
    import battery_ci
    importlib.reload(battery_ci)
    canon = battery_ci.canon
    # recibo integro (formato aninhado, como a Rodada G)
    payload = {"experimento": "H9", "job": "abc123", "veredito": "PASS"}
    rec = {"payload": payload,
           "selo_sha3_256": hashlib.sha3_256(canon(payload).encode()).hexdigest()}
    good = tmp_path / "good.json"; good.write_text(json.dumps(rec))
    battery_ci.FAILED.clear()
    battery_ci.verify_receipt(str(good))
    assert str(good) not in battery_ci.FAILED, "recibo aninhado integro deve PASSAR"
    # recibo adulterado: um campo mudado apos o selo
    rec["payload"]["veredito"] = "PASS_APOS_TAMPER"
    bad = tmp_path / "bad.json"; bad.write_text(json.dumps(rec))
    battery_ci.FAILED.clear()
    battery_ci.verify_receipt(str(bad))
    assert str(bad) in battery_ci.FAILED, "recibo aninhado adulterado deve FALHAR"
    # o recibo real da Rodada G, do repo, e INTEGRAL (selo sobre payload)
    d = json.load(open(os.path.join(os.path.dirname(__file__), "..",
                                    "experiments", "round_g_receipt.json")))
    assert hashlib.sha3_256(canon(d["payload"]).encode()).hexdigest() == d["selo_sha3_256"]
