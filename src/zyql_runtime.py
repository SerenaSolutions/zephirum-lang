"""ZYQL PRODUCTION RUNTIME (v1.8.0) — decisão trivalente como componente de produção.

API pública estável:
    from zyql_runtime import decide, Verdict
    r = decide(lambda x: x & 1, n=3, shots=512)   # r.verdict == Verdict.REFUSED
    r = decide(lambda x: 1)                        # r.verdict == Verdict.PERMIT

Garantias de produção:
  - Determinismo por seed (default 1701); mesma seed, mesmo resultado.
  - Toda decisão com Limite de erro Hoeffding declarado (r.error_bound).
  - 1 chamada de oráculo por decisão (+1 sonda clássica se constante).
  - Validação de entrada: erros levantam ValueError ANTES de gastar oráculo.
  - Recibo SHA3-256 opcional em cada decisão (selo offline verificável).
  - Sem estado global mutável; seguro em threads; zero prints no caminho da lib.

Limites declarados (docs/MATURITY.md): n prático <= 8 na fase-oráculo simulada;
decisões com oráculo caro devem usar backend IBM (via Serena Quantum API).
"""
import hashlib, json, logging, time
from dataclasses import dataclass, field, asdict
from enum import Enum
from zyql_quantum_gate import ZYQLQuantumGate, ghz_integrity, adaptive_margin

log = logging.getLogger("zyql")

class Verdict(Enum):
    PERMIT = 1
    DENY = 0
    REFUSED = "REFUSED"

@dataclass(frozen=True)
class Decision:
    verdict: Verdict
    p0: float
    mode: str
    error_bound: float
    oracle_calls: int
    shots: int
    n: int
    latency_ms: float
    receipt: dict = field(default=None, repr=False, compare=False)

class ConfigError(ValueError):
    """Erro de configuração do runtime (validação pré-oráculo)."""

def _validate(f, n, shots, seed):
    if not callable(f):
        raise ConfigError("oracle f precisa ser callable(x)->{0,1}")
    if not (1 <= n <= 8):
        raise ConfigError(f"n={n} fora do suporte de produção (1..8)")
    if not (16 <= shots <= 100_000):
        raise ConfigError(f"shots={shots} fora da banda suportada (16..100000)")
    if seed is not None and not isinstance(seed, int):
        raise ConfigError("seed precisa ser int ou None")

def decide(f, n=3, shots=2048, seed=1701, seal_path=None,
           epsilon=None, require_device_trust=False, device_shots=2048,
           previous_seal=None) -> Decision:
    """Decisão trivalente 1/0/REFUSED por interferência Deutsch-Jozsa.

    v1.9.0 — upgrades:
      epsilon: banda adaptativa (Hoeffding inverso). O veredito declara o erro.
      require_device_trust: porta GHZ primeiro; dispositivo inconfiável =>
        REFUSED por decoerência, SEM gastar oráculo (semântica inédita).
      previous_seal: cadeia de proveniência — o recibo sela o selo do anterior.
    """
    _validate(f, n, shots, seed)
    t0 = time.perf_counter()
    gate_result = None
    if require_device_trust:
        gate_result = ghz_integrity(n=n, shots=device_shots, seed=seed if seed is not None else 1701)
        if not gate_result["device_trusted"]:
            return Decision(verdict=Verdict.REFUSED, p0=0.0,
                            mode="REFUSED_DEVICE_DECOHERED (GHZ fidelity %.3f < %.2f)"
                                 % (gate_result["fidelity_ghz"], gate_result["threshold"]),
                            error_bound=1.0, oracle_calls=0, shots=0, n=n,
                            latency_ms=round((time.perf_counter()-t0)*1000, 3),
                            receipt=None)
    g = ZYQLQuantumGate(n, f)
    r = g.run_quantum(shots=shots, seed=seed if seed is not None else 1701, epsilon=epsilon)
    latency_ms = round((time.perf_counter() - t0) * 1000, 3)
    verdict = Verdict(r["decision"]) if r["decision"] in (1, 0) else Verdict.REFUSED
    receipt = None
    if seal_path:
        payload = {"verdict": verdict.value if verdict != Verdict.REFUSED else "REFUSED",
                   "p0": r["p0"], "shots": shots, "n": n, "seed": seed,
                   "mode": r["mode"], "error_bound": r["error_bound"],
                   "epsilon_declared": epsilon,
                   "device_gate": gate_result,
                   "previous_seal": previous_seal,
                   "oracle_calls": g.oracle_calls, "sealed_by": "zyql-runtime-1.9.0"}
        selo = hashlib.sha3_256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        receipt = {"payload": payload, "selo_sha3_256": selo}
        with open(seal_path, "w") as fh:
            json.dump(receipt, fh, indent=1)
        log.info("recibo selado: %s", seal_path)
    return Decision(verdict=verdict, p0=r["p0"], mode=r["mode"],
                    error_bound=r["error_bound"], oracle_calls=g.oracle_calls,
                    shots=shots, n=n, latency_ms=latency_ms, receipt=receipt)

def verify_receipt(path) -> bool:
    """Verificação offline do selo SHA3-256 de um recibo do runtime."""
    rec = json.load(open(path))
    payload = rec["payload"]
    ok = rec["selo_sha3_256"] == hashlib.sha3_256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return ok

def main(argv=None):
    """CLI: zyql-decide --oracle balanced|one|zero --n 3 --shots 512 [--seed S] [--seal PATH]"""
    import argparse
    p = argparse.ArgumentParser(prog="zyql-decide", description="ZYQL trivalent decision runtime")
    p.add_argument("--oracle", choices=["one", "zero", "balanced"], default="balanced")
    p.add_argument("--n", type=int, default=3); p.add_argument("--shots", type=int, default=512)
    p.add_argument("--seed", type=int, default=1701); p.add_argument("--seal", default=None)
    a = p.parse_args(argv)
    f = {"one": lambda x: 1, "zero": lambda x: 0, "balanced": lambda x: x & 1}[a.oracle]
    r = decide(f, n=a.n, shots=a.shots, seed=a.seed, seal_path=a.seal)
    print(f"veredito: {r.verdict.value if r.verdict.value != 'REFUSED' else 'REFUSED'} | "
          f"p0={r.p0:.4f} | erro<={r.error_bound:.2e} | oraculo:{r.oracle_calls} | {r.latency_ms}ms")
    return 0 if r.verdict != Verdict.REFUSED else 2

if __name__ == "__main__":
    raise SystemExit(main())


def verify_chain(paths):
    """v1.9.0 — cadeia de proveniência: recibo[i].payload.previous_seal == recibo[i-1].selo."""
    seals = []
    for p in paths:
        rec = json.load(open(p))
        if not verify_receipt(p):
            return {"chain_ok": False, "broken_at": p, "reason": "selo interno rompido"}
        seals.append(rec["selo_sha3_256"])
    for i in range(1, len(paths)):
        rec = json.load(open(paths[i]))
        prev = rec["payload"].get("previous_seal")
        if prev != seals[i - 1]:
            return {"chain_ok": False, "broken_at": paths[i],
                    "reason": "elos nao batem com recibo anterior"}
    return {"chain_ok": True, "links": len(paths)}
