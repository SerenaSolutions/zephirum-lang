"""
Verificador offline da prova de fogo ZYQL/ZEPHIRUM.

Não confia em quem gerou o recibo: recomputa o selo SHA3-256 e reconfere cada
veredito a partir dos counts crus, usando a mesma regra declarada no recibo.

Uso:  python3 experiments/verificar_prova_de_fogo.py experiments/prova_de_fogo_receipt.json
Saida: 0 se íntegro e coerente; 1 se divergir.
"""
import hashlib
import json
import math
import sys

N = 3


def selo(obj) -> str:
    canon = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_256(canon.encode()).hexdigest()


def p_zero(counts):
    tot = sum(counts.values())
    return counts.get("0" * N, 0) / tot if tot else 0.0


def p_um(counts):
    tot = sum(counts.values())
    return counts.get("1", 0) / tot if tot else 0.0


def main(path):
    rec = json.load(open(path))
    falhas = []

    # 1. selo
    corpo = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
    if selo(corpo) != rec.get("selo_sha3_256"):
        falhas.append("SELO NAO BATE: recibo alterado depois da selagem")

    # 2. banda declarada
    shots = rec["shots"]
    eps = rec["epsilon"]
    b = math.sqrt(math.log(2 / eps) / (2 * shots))
    if abs(b - rec["banda_hoeffding"]) > 1e-5:
        falhas.append(f"BANDA DIVERGENTE: recibo {rec['banda_hoeffding']} vs recomputado {round(b,6)}")

    # 3. cada oraculo reconferido do zero
    c = rec["counts"]
    for orac in ("const0", "const1", "balanced"):
        cz = p_zero(c[f"{orac}_interf"])
        cu = p_um(c[f"{orac}_f0"])
        v = str(rec["vereditos"][orac]["veredito"])

        if cz >= 1 - b:
            classe = "CONSTANTE"
        elif cz <= b:
            classe = "BALANCEADO"
        else:
            classe = "INDEFINIDA"

        if classe == "BALANCEADO" and v != "REFUSED":
            falhas.append(f"{orac}: p_zero={cz:.4f} indica balanceado, mas veredito foi {v}")
        if classe == "INDEFINIDA" and v != "REFUSED":
            falhas.append(f"{orac}: p_zero={cz:.4f} dentro da banda, mas veredito foi {v}")
        if classe == "CONSTANTE" and orac != "balanced":
            esperado = "1" if cu >= 1 - b else ("0" if cu <= b else "REFUSED")
            if v != esperado:
                falhas.append(f"{orac}: f(0) p_um={cu:.4f} implica {esperado}, mas veredito foi {v}")
        if orac == "balanced" and classe == "CONSTANTE":
            falhas.append("balanced: leitura diz constante, contradiz o oraculo declarado")

    # 4. porta GHZ manda
    cg = c["ghz3"]
    tot = sum(cg.values())
    fid = (cg.get("000", 0) + cg.get("111", 0)) / tot
    if abs(fid - rec["porta_ghz"]["fidelidade"]) > 1e-3:
        falhas.append(f"GHZ: fidelidade recibo {rec['porta_ghz']['fidelidade']} vs recomputada {round(fid,4)}")
    if fid < 0.80:
        for orac in ("const0", "const1", "balanced"):
            if str(rec["vereditos"][orac]["veredito"]) != "REFUSED":
                falhas.append(f"{orac}: dispositivo suspeito (fid {fid:.4f}) mas veredito nao foi REFUSED")

    print(f"recibo : {path}")
    print(f"backend: {rec['backend']} | job: {rec['job_id']} | shots: {shots}")
    print(f"selo   : {rec['selo_sha3_256']}")
    print(f"GHZ    : fidelidade recomputada {round(fid,4)}")
    if falhas:
        print("\nREPROVADO:")
        for f in falhas:
            print("  -", f)
        return 1
    print("\nAPROVADO: selo integro e todos os vereditos reconferem pelos counts crus.")
    return 0


if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else "experiments/prova_de_fogo_receipt.json"
    sys.exit(main(alvo))
