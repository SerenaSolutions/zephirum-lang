# -*- coding: utf-8 -*-
"""RODADA PONTE KET — a primeira ponte entre linguagens quânticas brasileiras.

Circuito construido e executado NA KET (simulador local KBW, 1024 medicoes),
evidencia alimentada no PORTAO DE DECISAO TRIVALENTE da ZEPHIRUM com banda
declarada, veredito selado em cadeia Z-QEA. Hipotese testada (refutavel):
"H da Ket produz bit uniformemente aleatorio" — p0 fora da banda => hipotese
REFUTADA com recibo.
"""
import json, os, sys, hashlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)
from zyql_quantum_gate import adaptive_margin_family
from ket import Process, Quant, H, CNOT, measure

N = 1024
UNS = 0
for _ in range(N):
    p = Process()
    q = p.alloc(2)
    H(q[0])
    CNOT(q[0], q[1])
    m = measure(q[0]).value
    UNS += 1 if m == 0 else 0
p0 = UNS / N
margem = adaptive_margin_family(0.05, N, family=1)
if abs(p0 - 0.5) <= margem:
    veredito = "1"
    motivo = "bit da Ket e uniforme dentro da banda declarada"
elif abs(p0 - 0.5) <= 2 * margem:
    veredito = "REFUSED"
    motivo = "na zona cinzenta: sem direito de afirmar"
else:
    veredito = "0"
    motivo = "vies detectado: hipotese refutada com recibo"

rec = {
    "spec": "Z-QEA/2.2", "modulo": "RODADA PONTE KET",
    "data": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "protocolo": ("Primeira ponte entre linguagens quanticas brasileiras: circuito Bell "
                  "construido e executado NA LINGUAGEM KET (v0.10.4.1, simulador local KBW, "
                  "%d medicoes independentes, processo novo por medida); p0 observado "
                  "testado contra hipotese refutavel de uniformidade pelo portao trivalente "
                  "ZEPHIRUM com banda adaptativa declarada antes do resultado" % N),
    "evidencia": {"fonte": "Ket v0.10.4.1 (linguagem quantica brasileira, KBW local)",
                  "circuito": "Bell: H(q0), CNOT(q0,q1), measure(q0)",
                  "shots": N, "p0_observado": round(p0, 4),
                  "banda_margem": round(margem, 4), "hipotese_nula": 0.5},
    "veredito": veredito, "motivo": motivo,
    "previous_seal": json.load(open(os.path.join(HERE, "round_dc_receipt.json")))["selo_sha3_256"],
    "receipt_id": "ponte-ket-" + hashlib.sha3_256(str(p0).encode()).hexdigest()[:8],
}
rec["selo_sha3_256"] = hashlib.sha3_256(json.dumps({k: v for k, v in rec.items()}, sort_keys=True, ensure_ascii=True, default=str).encode()).hexdigest()
json.dump(rec, open(os.path.join(HERE, "round_ket_receipt.json"), "w"), ensure_ascii=True, indent=1)
print("Ket (1024 medidas da casa brasileira): p0 = %.4f (banda +/- %.4f)" % (p0, margem))
print("veredito trivalente:", veredito, "-", motivo)
print("selo:", rec["selo_sha3_256"][:16], "| encadeado em", rec["previous_seal"][:12])
