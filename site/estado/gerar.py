#!/usr/bin/env python3
"""Gera site/estado/index.html a partir dos recibos em dados/.

O site do projeto e estatico (vercel.json: outputDirectory "site", sem build),
entao o HTML gerado e versionado, e o selo SHA3-256 cobre os arquivos de origem.
Regenerar depois de qualquer execucao nova:

    python3 site/estado/gerar.py

Uso no veredito: nada aqui e digitado a mao; todo numero vem de recibo.
"""
import hashlib
import json
import pathlib
from datetime import datetime, timezone

BASE = pathlib.Path(__file__).resolve().parent
RECIBO = BASE / "dados" / "recibo_hardware_20261114T164802.json"
ENVELOPE = BASE / "dados" / "envelope_largura.json"


def selo(*arquivos):
    """SHA3-256 deterministico: nome e conteudo de cada fonte, nesta ordem."""
    h = hashlib.sha3_256()
    for a in arquivos:
        h.update(a.name.encode() + b"\n" + a.read_bytes() + b"\n")
    return h.hexdigest()


def linhas_dj(dj):
    saida = []
    for chave, etiqueta in (("constante_0", "Constante f = 0"),
                            ("balanceado_paridade", "Balanceado, paridade")):
        c = dj["casos"][chave]
        v = c["veredito"]
        decisao = v["decision"] if v["decision"] != "REFUSED" else "REFUSED · " + v["refusal_reason"]
        saida.append(
            "<tr><td>%s</td><td class=\"num\">%.4f</td>"
            "<td class=\"num\">[%.4f; %.4f]</td><td class=\"dec\">%s</td>"
            "<td class=\"mono\">%s</td></tr>" % (etiqueta, c["p0"], v["p_lo"], v["p_hi"], decisao, c["job_id"])
        )
    return "".join(saida)


def barras_ghz(env):
    saida = []
    for chave in ("ghz_10", "ghz_20", "ghz_30", "ghz_50", "ghz_80", "ghz_100"):
        c = env["casos"][chave]
        p = c["p_00_mais_11"] or 0.0
        nq = int(chave.split("_")[1])
        saida.append(
            "<div class=\"bar\"><span class=\"q\">%d q</span>"
            "<i style=\"width:%.1f%%\"></i><span class=\"val num\">%.3f</span></div>"
            % (nq, max(1.0, p * 100), p)
        )
    return "".join(saida)


def main():
    dj = json.loads(RECIBO.read_text(encoding="utf-8"))
    env = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    cal = dj["calibracao"]
    s = selo(RECIBO, ENVELOPE)
    agora = datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M %Z")

    html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Z# — estado verificável</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#0b0b0c;color:#ededed;font:16px/1.65 -apple-system,system-ui,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}}
main{{max-width:56rem;margin:0 auto;padding:4.5rem 1.5rem 6rem}}
h1{{font-size:clamp(1.9rem,4vw,2.6rem);font-weight:650;letter-spacing:-.02em;margin:0 0 .4rem}}
h2{{font-size:.78rem;text-transform:uppercase;letter-spacing:.14em;color:#8f8f96;font-weight:600;margin:3.5rem 0 1rem;border-top:1px solid #232327;padding-top:1.1rem}}
p{{color:#b9b9c0;max-width:44rem}}
.lead{{color:#9a9aa2;font-size:1.02rem;margin:0 0 2.5rem}}
table{{width:100%;border-collapse:collapse;font-size:.92rem;margin-top:.4rem}}
th{{text-align:left;font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:#7d7d85;font-weight:600;padding:0 0 .6rem}}
td{{padding:.75rem .8rem .75rem 0;border-top:1px solid #1e1e22;vertical-align:top}}
.num{{font-variant-numeric:tabular-nums;color:#e8e8ec;white-space:nowrap}}
.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.78rem;color:#8a8a92;word-break:break-all}}
.dec{{color:#fff;font-weight:600;white-space:nowrap}}
.bar{{display:grid;grid-template-columns:3.4rem 1fr 3.4rem;align-items:center;gap:.9rem;margin:.5rem 0}}
.bar i{{display:block;height:.55rem;background:#3b6f4a;border-radius:2px;min-width:2px}}
.bar .q{{color:#8f8f96;font-size:.85rem}}
.bar .val{{text-align:right;color:#e8e8ec;font-size:.88rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(9.5rem,1fr));gap:1px;background:#1e1e22;border:1px solid #1e1e22;margin-top:.5rem}}
.cell{{background:#0b0b0c;padding:1rem}}
.cell b{{display:block;font-size:.7rem;text-transform:uppercase;letter-spacing:.09em;color:#7d7d85;font-weight:600;margin-bottom:.35rem}}
.cell span{{font-size:1.25rem;font-variant-numeric:tabular-nums}}
ul{{color:#b9b9c0;padding-left:1.1rem}}li{{margin:.3rem 0}}
footer{{margin-top:4rem;padding-top:1.2rem;border-top:1px solid #232327;color:#6f6f77;font-size:.8rem}}
code{{font-family:ui-monospace,monospace;font-size:.82rem;color:#cfd4c9}}
a{{color:#8fb59a}}
</style></head><body><main>
<h1>Z# — estado verificável</h1>
<p class="lead">Tudo nesta página é gerado a partir de recibos de execução. Nenhum número foi digitado à mão. Gerado em {agora}.</p>

<h2>1. Decisão em três saídas</h2>
<p>O veredito sai <code>1</code>, <code>0</code> ou <code>REFUSED</code>. Decidir exige que o limite do intervalo atravesse a banda declarada; a média sozinha não decide. Cota de erro igual a 1 recusa (<code>ERROR_BOUND_AT_LEAST_ONE</code>), banda maior que 0,5 recusa (<code>BAND_TOO_WIDE</code>), e estimativa fora da banda com intervalo dentro dela recusa (<code>INTERVAL_INSIDE_BAND</code>).</p>

<h2>2. Hardware real, {dj['backend']}, {dj['shots']} disparos</h2>
<table><thead><tr><th>Caso</th><th>p0</th><th>Intervalo</th><th>Veredito</th><th>Job</th></tr></thead>
<tbody>{linhas_dj(dj)}</tbody></table>

<h2>3. Envelope de largura (GHZ, 1024 disparos)</h2>
<p>Fração de medidas em que todos os qubits saem iguais. É o teste mais simples de coerência: se a informação sobrevive, os qubits concordam.</p>
{barras_ghz(env)}

<h2>4. Estado da máquina na execução</h2>
<div class="grid">
<div class="cell"><b>Aparelho</b><span>{cal['backend_id']}</span></div>
<div class="cell"><b>Qubits</b><span>{cal['n_qubits']}</span></div>
<div class="cell"><b>T1 mediano</b><span>{cal['t1_mediano']:.1f} µs</span></div>
<div class="cell"><b>T2 mediano</b><span>{cal['t2_mediano']:.1f} µs</span></div>
<div class="cell"><b>Erro de leitura</b><span>{cal['erro_leitura_mediano']*100:.2f}%</span></div>
<div class="cell"><b>Erro porta 2q</b><span>{cal['erro_porta_2q_mediano']*100:.2f}%</span></div>
</div>
<p class="mono">calibração medida em {cal['epoch']}</p>

<h2>5. O que esta página não afirma</h2>
<ul>
<li>Nenhuma vantagem sobre método clássico. Nada aqui é sobre velocidade.</li>
<li>Nenhum endosso de fornecedor e nenhuma certificação.</li>
<li>Nada acima de 30 qubits produziu sinal utilizável: a partir daí o veredito honesto é <code>REFUSED</code>.</li>
<li>O limite declarado de disparos, a partir do qual o gate começa a decidir, ainda não foi medido.</li>
</ul>

<footer>Selo do conteúdo (SHA3-256 dos dois arquivos em <code>site/estado/dados/</code>):<br>
<span class="mono">{s}</span><br>
Fontes: <code>dados/recibo_hardware_20261114T164802.json</code>, <code>dados/envelope_largura.json</code>.</footer>
</main></body></html>"""

    destino = BASE / "index.html"
    destino.write_text(html, encoding="utf-8")
    print("gerado:", destino, "| selo", s[:24], "| bytes", len(html))


if __name__ == "__main__":
    main()
