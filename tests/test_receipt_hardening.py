# SPDX-License-Identifier: Apache-2.0
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from qroute import receipt


def test_nonce_unico_e_seq_crescente(tmp_path):
    a = tmp_path / "r.json"
    r1 = receipt.sela({"veredito": 0}, str(a))
    r2 = receipt.sela({"veredito": 1}, str(a), receipt.le_anterior(str(a)))
    assert r1["nonce"] != r2["nonce"]
    assert r2["seq"] == r1["seq"] + 1  # mesma corrente, arquivo reescrito


def test_encadeamento_ok(tmp_path):
    a = tmp_path / "r1.json"; b = tmp_path / "r2.json"
    r1 = receipt.sela({"v": 1}, str(a))
    r2 = receipt.sela({"v": 0}, str(b), r1["sha3_256"], seq=r1["seq"] + 1)
    v = receipt.verifica_encadeamento(str(b), anterior=str(a), seq_esperado=r1["seq"] + 1)
    assert r2["seq"] == r1["seq"] + 1
    assert v["ok"], v["motivos"]


def test_prev_hash_adulterado_detectado(tmp_path):
    a = tmp_path / "r1.json"; b = tmp_path / "r2.json"
    r1 = receipt.sela({"v": 1}, str(a))
    receipt.sela({"v": 0}, str(b), "0" * 64)
    v = receipt.verifica_encadeamento(str(b), anterior=str(a))
    assert not v["ok"] and "prev_sha3_divergente" in v["motivos"]


def test_recibo_sem_nonce_e_rejeitado(tmp_path):
    p = tmp_path / "legado.json"
    p.write_text(json.dumps({"veredito": 0, "seq": 1}), encoding="utf-8")
    v = receipt.verifica_encadeamento(str(p))
    assert "nonce_ausente" in v["motivos"]
