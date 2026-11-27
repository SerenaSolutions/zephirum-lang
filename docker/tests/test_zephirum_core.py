# SPDX-License-Identifier: Apache-2.0
"""Testes de propriedade do ZEPHIRUM Core.

Para cada regra: (1) eliminacao com recibo valido, (2) fallback/resultado exato,
(3) REFUSED explicito em caso indecidivel. Mais: recibo adulterado e fail-closed.
"""
import unittest
from fractions import Fraction

from zephirum_core import cert, qasm3, zca
from zephirum_core.backends import ibm
from zephirum_core.exact import parse


class TestAritmeticaExata(unittest.TestCase):
    def test_nenhum_float_no_resultado(self):
        for bruto in ("1/3", "0.25", "7", "2,5"):
            valor = parse(bruto)
            self.assertIsInstance(valor, Fraction)
            self.assertNotIsInstance(valor, float)

    def test_denominador_zero_recusa(self):
        self.assertIsNone(parse("1/0"))

    def test_soma_exata_sem_perda(self):
        self.assertEqual(parse("1/3") + parse("2/3"), 1)


class TestZCARegras(unittest.TestCase):
    def test_frac_eq_elimina(self):
        r = zca.executar("frac_eq", {"a": "1/3", "b": "2/6"})
        self.assertEqual(r["veredito"], 1)
        self.assertEqual(r["resultado"]["diferenca"], "0")
        self.assertEqual(cert.verificar(r["cert"], r["cert"]["hash"])["ok"], True)

    def test_frac_eq_diferentes(self):
        self.assertEqual(zca.executar("frac_eq", {"a": "1/3", "b": "1/4"})["veredito"], 0)

    def test_proporcao_exata(self):
        r = zca.executar("proporcao", {"a": "2", "b": "5", "c": "7"})
        self.assertEqual(r["resultado"]["x"], "35/2")

    def test_proporcao_indefinida_recusa(self):
        self.assertEqual(zca.executar("proporcao", {"a": "0", "b": "5", "c": "7"})["veredito"], "REFUSED")

    def test_porcento_exato(self):
        self.assertEqual(zca.executar("porcento", {"p": "15", "v": "240"})["resultado"]["valor"], "36")

    def test_limite_acima(self):
        r = zca.executar("limite", {"valor": "1.2", "limite": "1"})
        self.assertEqual(r["veredito"], 1)
        self.assertEqual(r["resultado"]["margem"], "1/5")

    def test_limite_entrada_hostil_recusa(self):
        r = zca.executar("limite", {"valor": "abc", "limite": "1"})
        self.assertEqual(r["veredito"], "REFUSED")
        self.assertTrue(r["ref"])

    def test_prazo_vencido(self):
        r = zca.executar("prazo", {"validade": "2026-01-01", "hoje": "2026-11-21"})
        self.assertEqual(r["veredito"], 1)
        self.assertEqual(r["resultado"]["situacao"], "VENCIDO")

    def test_ppm_exato(self):
        r = zca.executar("ppm_mgm3", {"ppm": "25", "massa_molar": "46.01"})
        self.assertEqual(r["resultado"]["mg_m3"], "23005/489")
        self.assertIn("convencao", r["resultado"])

    def test_regra_desconhecida_recusa(self):
        self.assertEqual(zca.executar("nao_existe", {})["veredito"], "REFUSED")


class TestRecibo(unittest.TestCase):
    def test_adulteracao_recusada(self):
        r = zca.executar("limite", {"valor": "1.2", "limite": "1"})
        adulterado = dict(r["cert"])
        adulterado["veredito"] = 0
        v = cert.verificar(adulterado, r["cert"]["hash"])
        self.assertFalse(v["ok"])
        self.assertEqual(v["veredito"], 0)

    def test_hash_invalido_recusa(self):
        self.assertEqual(cert.verificar({"a": 1}, "xyz")["veredito"], "REFUSED")

    def test_mesmo_conteudo_mesmo_hash(self):
        self.assertEqual(cert.digest({"b": 1, "a": 2}), cert.digest({"a": 2, "b": 1}))


class TestPonteQasm3(unittest.TestCase):
    BELL = "OPENQASM 3.0;\nqubit[2] q;\nh q[0];\ncx q[0],q[1];\nmeasure q -> c;"

    def test_clifford_nao_precisa_de_qpu(self):
        self.assertEqual(qasm3.decidir(self.BELL)["veredito"], 1)

    def test_nao_clifford_exige_computacao(self):
        self.assertEqual(qasm3.decidir("OPENQASM 3.0;\nqubit[1] q;\nh q[0];\nt q[0];")["veredito"], 0)

    def test_angulo_simbolico_clifford(self):
        self.assertEqual(qasm3.decidir("OPENQASM 3.0;\nqubit[1] q;\nrz(pi/2) q[0];")["veredito"], 1)

    def test_angulo_arbitrario_nao_clifford(self):
        self.assertEqual(qasm3.decidir("OPENQASM 3.0;\nqubit[1] q;\nrz(0.3) q[0];")["veredito"], 0)

    def test_porta_desconhecida_recusa(self):
        self.assertEqual(qasm3.decidir("OPENQASM 3.0;\nqubit[1] q;\nfrobnicate q[0];")["veredito"], "REFUSED")

    def test_programa_vazio_recusa(self):
        self.assertEqual(qasm3.decidir("")["veredito"], "REFUSED")


class TestBackendIBMFailClosed(unittest.TestCase):
    def test_sem_token_recusa(self):
        # Sem token -> IBM-401; com token mas sem qiskit -> IBM-503. Ambos fail-closed.
        r = ibm.submeter("OPENQASM 3.0;\nqubit[1] q;\nt q[0];")
        self.assertEqual(r["veredito"], "REFUSED")
        self.assertIn(r["codigo"], ("IBM-401", "IBM-403", "IBM-503"))

    def test_portao_de_cota_barra_clifford(self):
        r = ibm.ensaio(TestPonteQasm3.BELL)
        self.assertEqual(r["veredito"], "REFUSED")
        self.assertEqual(r["permitido_para_qpu"], False)

    def test_portao_libera_nao_clifford(self):
        r = ibm.ensaio("OPENQASM 3.0;\nqubit[1] q;\nt q[0];")
        self.assertEqual(r["veredito"], "ENSAIO")
        self.assertEqual(r["permitido_para_qpu"], True)


if __name__ == "__main__":
    unittest.main()
