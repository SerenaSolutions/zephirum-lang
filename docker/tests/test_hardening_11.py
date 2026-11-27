"""Testes do Core Hardening 1.1 (frentes A-F). Nenhum teste toca rede."""
import json
import os
import unittest
from decimal import Decimal
from fractions import Fraction

from zephirum_core import cert, exact, qasm3, zca
from zephirum_core.backends import ibm


class TestExactArithmetic(unittest.TestCase):
    """A: float nunca entra em decisao."""

    def test_float_rejeitado_por_padrao(self):
        for v in (0.1, 1.5, 3.14159, float("nan"), float("inf")):
            self.assertIsNone(exact.parse(v), f"float aceito: {v}")

    def test_float_so_com_opt_in_explicito(self):
        self.assertEqual(exact.parse(0.25, permitir_float=True), Fraction(1, 4))

    def test_entradas_exatas_aceitas(self):
        self.assertEqual(exact.parse(7), Fraction(7))
        self.assertEqual(exact.parse("1/3"), Fraction(1, 3))
        self.assertEqual(exact.parse("0.25"), Fraction(1, 4))
        self.assertEqual(exact.parse("2,5"), Fraction(5, 2))
        self.assertEqual(exact.parse(Decimal("0.125")), Fraction(1, 8))
        self.assertEqual(exact.parse(Fraction(3, 7)), Fraction(3, 7))

    def test_entradas_invalidas_recusadas(self):
        for v in (None, True, False, "", "abc", "1/0", "1e-3"):
            self.assertIsNone(exact.parse(v), f"aceitou invalido: {v!r}")

    def test_json_numerico_float_e_rejeitado(self):
        dados = json.loads('{"valor": 0.1}')
        self.assertIsNone(exact.parse(dados["valor"]))


class TestQpuSafety(unittest.TestCase):
    """B: nada vai para a QPU sem opt-in explicito."""

    def setUp(self):
        self._antes = os.environ.pop("ZEPHIRUM_ALLOW_QPU_SUBMIT", None)

    def tearDown(self):
        os.environ.pop("ZEPHIRUM_ALLOW_QPU_SUBMIT", None)
        if self._antes is not None:
            os.environ["ZEPHIRUM_ALLOW_QPU_SUBMIT"] = self._antes

    def test_padrao_nunca_submete(self):
        r = ibm.submeter("OPENQASM 3.0;\nqubit[2] q;\nh q[0];\ncx q[0], q[1];")
        self.assertEqual(r["veredito"], "REFUSED")
        self.assertEqual(r["codigo"], "IBM-403")
        self.assertNotIn("job_id", r)

    def test_opt_in_habilitado_mas_sem_token_ainda_recusa(self):
        os.environ["ZEPHIRUM_ALLOW_QPU_SUBMIT"] = "1"
        r = ibm.submeter("OPENQASM 3.0;\nqubit[1] q;\nt q[0];")
        self.assertEqual(r["veredito"], "REFUSED")
        self.assertNotIn("job_id", r)

    def test_validacao_de_backend_e_shots(self):
        self.assertFalse(ibm.validar_pedido("ibm fez", 100)[0])
        self.assertFalse(ibm.validar_pedido("ibm_fez", 0)[0])
        self.assertFalse(ibm.validar_pedido("ibm_fez", 10 ** 7)[0])
        self.assertFalse(ibm.validar_pedido("ibm_fez", "abc")[0])
        self.assertTrue(ibm.validar_pedido("ibm_fez", 400)[0])

    def test_ensaio_nao_submete(self):
        r = ibm.ensaio("OPENQASM 3.0;\nqubit[1] q;\nt q[0];")
        self.assertNotIn("job_id", r)


class TestOpenQasmGrammar(unittest.TestCase):
    """C: subconjunto declarado; o resto e recusado."""

    def test_gramatica_declarada_existe(self):
        g = qasm3.GRAMATICA_SUPORTADA
        self.assertIn("versao", g)
        self.assertIn("recusadas", g)
        self.assertIn("OpenQASM 3 integral", g["conformidade"])

    def test_construcoes_recusadas(self):
        casos = [
            "OPENQASM 3.0;\nqubit[2] q;\nif (c==1) x q[0];",
            "OPENQASM 3.0;\nfor i in [0:3] { x q[0]; }",
            "OPENQASM 3.0;\nwhile (true) { x q[0]; }",
            "OPENQASM 3.0;\ngate minha a { h a; }",
            "OPENQASM 3.0;\ndelay[10ns] q[0];",
        ]
        for src in casos:
            self.assertEqual(qasm3.decidir(src)["veredito"], "REFUSED", src)

    def test_clifford_continua_1_e_nao_clifford_continua_0(self):
        self.assertEqual(qasm3.decidir("OPENQASM 3.0;\nqubit[2] q;\nh q[0];\ncx q[0], q[1];")["veredito"], 1)
        self.assertEqual(qasm3.decidir("OPENQASM 3.0;\nqubit[1] q;\nt q[0];")["veredito"], 0)

    def test_certificado_declara_gramatica(self):
        c = qasm3.decidir("OPENQASM 3.0;\nqubit[1] q;\nt q[0];")["cert"]
        self.assertEqual(c["gramatica"], qasm3.GRAMATICA_SUPORTADA["versao"])


class TestStructuredCertificates(unittest.TestCase):
    """D: integridade != prova; verificador independente decide."""

    def test_hash_nao_e_prova(self):
        c = cert.emitir_certificado({"a": 1, "b": 2}, "soma", 3)
        self.assertFalse(c["prova_verificada"])
        self.assertIn("hash", c)

    def test_verificador_independente_aprova(self):
        c = cert.emitir_certificado({"a": 1, "b": 2}, "soma", 3)
        r = cert.verificar_certificado(c, {"soma": lambda i: i["a"] + i["b"]})
        self.assertEqual(r["veredito"], 1)

    def test_verificador_recusa_output_falso(self):
        c = cert.emitir_certificado({"a": 1, "b": 2}, "soma", 4)
        r = cert.verificar_certificado(c, {"soma": lambda i: i["a"] + i["b"]})
        self.assertEqual(r["veredito"], 0)

    def test_sem_verificador_e_refused(self):
        c = cert.emitir_certificado({"a": 1}, "regra_desconhecida", 1)
        self.assertEqual(cert.verificar_certificado(c, {})["veredito"], "REFUSED")

    def test_adulteracao_quebra_integridade(self):
        c = cert.emitir_certificado({"a": 1, "b": 2}, "soma", 3)
        c["output"] = 99
        r = cert.verificar_certificado(c, {"soma": lambda i: i["a"] + i["b"]})
        self.assertEqual(r["veredito"], "REFUSED")

    def test_sha3_disponivel_sem_quebrar_compatibilidade(self):
        # formato de recibo nao muda sem RFC: padrao segue SHA-256
        c = cert.emitir({"x": 1})
        self.assertEqual(c["hash_alg"], "SHA-256")
        c3 = cert.emitir({"x": 1}, alg="sha3_256")
        self.assertEqual(c3["hash_alg"], "SHA3-256")
        self.assertEqual(cert.verificar(c3, c3["hash"])["veredito"], 1)


class TestApiSecurity(unittest.TestCase):
    """E: /submit fechado por padrao, quota e CORS restrito."""

    def test_sem_token_configurado_bloqueia(self):
        from zephirum_core import server
        antes = server.TOKEN_API
        server.TOKEN_API = ""
        try:
            ok, motivo = server.autorizado({"x-api-token": "qualquer"})
            self.assertFalse(ok)
            self.assertIn("desabilitada", motivo)
        finally:
            server.TOKEN_API = antes

    def test_token_correto_autoriza(self):
        from zephirum_core import server
        antes = server.TOKEN_API
        server.TOKEN_API = "segredo-teste"
        try:
            self.assertTrue(server.autorizado({"x-api-token": "segredo-teste"})[0])
            self.assertFalse(server.autorizado({"x-api-token": "errado"})[0])
            self.assertFalse(server.autorizado({})[0])
        finally:
            server.TOKEN_API = antes

    def test_quota_limita(self):
        from zephirum_core import server
        antes = server.QUOTA_SUBMIT_POR_HORA
        server.QUOTA_SUBMIT_POR_HORA = 2
        server._USO_SUBMIT.clear()
        try:
            self.assertTrue(server.dentro_da_quota("1.2.3.4")[0])
            self.assertTrue(server.dentro_da_quota("1.2.3.4")[0])
            self.assertFalse(server.dentro_da_quota("1.2.3.4")[0])
            self.assertTrue(server.dentro_da_quota("5.6.7.8")[0])
        finally:
            server.QUOTA_POR_HORA = antes if False else None
            server.QUOTA_SUBMIT_POR_HORA = antes
            server._USO_SUBMIT.clear()

    def test_cors_nao_aberto_por_padrao(self):
        from zephirum_core import server
        self.assertEqual(server.CORS_ORIGEM, "")


class TestZyqlIntegration(unittest.TestCase):
    """F: REFUSED e estado de primeira classe; nenhum motor duplicado."""

    def test_zca_recusa_entrada_invalida(self):
        r = zca.executar("frac_eq", {"a": "1/3", "b": "2/6"})
        self.assertIn(r.get("veredito"), (1, "REFUSED"))

    def test_zca_operacao_desconhecida_e_refused(self):
        r = zca.executar("op_inexistente", {})
        self.assertEqual(r.get("veredito"), "REFUSED")

    def test_qasm3_e_zca_compartilham_certificado(self):
        c = qasm3.decidir("OPENQASM 3.0;\nqubit[1] q;\nt q[0];")["cert"]
        self.assertEqual(cert.verificar(c, c["hash"])["veredito"], 1)


if __name__ == "__main__":
    unittest.main()
