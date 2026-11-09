# Anúncio institucional — entrada do ZEPHIRUM no ecossistema Qiskit

**Para publicação por Serena Quantum Solutions · 2026-11-09**

---

O ZEPHIRUM passa a integrar o ecossistema Qiskit. O pull request #1433 foi mergeado no
repositório `Qiskit/ecosystem` em 9 de novembro de 2026, commit `d327b86`, com revisão e
edições do mantenedor Luciano Bello.

O ZEPHIRUM é uma linguagem de decisão trivalente: cada veredito é `1`, `0` ou `REFUSED`,
acompanhado de incerteza declarada e de um recibo verificável. A tese é simples e
desconfortável: a maior parte das perguntas feitas a um computador quântico não deveria
chegar ao computador quântico antes de passar por um portão que saiba dizer não.

Sobre o que este marco é, e o que não é, para não haver mal-entendido:

**É** o reconhecimento de que o projeto existe, é público, tem licença clara e se integra
às ferramentas do ecossistema. A entrada é registrada como categoria SDK, maturidade
experimental, estágio inicial. Assinamos essa classificação porque ela é verdadeira.

**Não é** certificação da IBM, nem validação da linguagem pela comunidade Qiskit, nem
selo de qualidade científica. O que foi incorporado é um arquivo de metadado. A semântica,
os recibos e os resultados seguem sujeitos a quem quiser refutá-los.

Uma precisão que evita mal-entendido: o catálogo lista **ZEPHIRUM**, e descreve o ZYQL
como seu núcleo de decisão. Isso não significa que o ZYQL tenha sido listado como projeto
separado. Sendo exato: entrou um projeto, descrito em uma entrada, com um núcleo nomeado
na descrição.

O que já está publicado e verificável: um protocolo de validação selado antes da execução,
com sete hipóteses falsificáveis e 3630 casos executados, sem
contravenção; uma suíte de 222 testes; e uma demonstração executável da integração com
Qiskit, incluindo controle negativo.

O que ainda não existe e não será anunciado como se existisse: assinatura criptográfica
dos recibos, reprodução independente por terceiro e estudo estatístico em hardware.

Crédito devido: Luciano Bello, pela revisão e pelo merge; à comunidade Qiskit, pela
manutenção de um ecossistema onde um projeto de fora dos grandes centros pode entrar
sendo examinado em vez de aceito por cortesia.

Links da entrada, todos verificados em 09/11/2026 (7 de 7 respondendo):
repositório, documentação, site, PyPI, perfil de publicador, shortlink do catálogo
e DOI no Zenodo.

Repositório: <https://github.com/SerenaSolutions/zephirum-lang>
Validação: <https://zephirum.vercel.app/validacao>

*Perguntar primeiro. Provar depois. Computar por último.*
