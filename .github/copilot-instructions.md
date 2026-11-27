# Regras do repositório ZEPHIRUM (SerenaSolutions)

Este é o repositório real: https://github.com/SerenaSolutions/zerum
Linguagem: ZEPHIRUM (ASK/CONTRACT/MODEL). Núcleo em Python puro (stdlib).

## Invariantes que nenhum agente pode violar
1. Semântica trivalente: TRUE / FALSE / Z (Z = UNKNOWN). Z nunca vira booleano.
2. Par.12: recusa explícita é resposta de primeira classe; nunca excepção engolida.
3. Aritmética exacta (Fraction) no núcleo; float apenas em camadas declaradas.
4. Proof → Compute: forma fechada antes de execução; orçamento em unidades.
5. Nenhuma alegação sem teste no mesmo commit. Nenhum resultado, benchmark ou job ID fabricado.
6. Nenhum fallback silencioso de backend; toda troca fica no recibo.
7. Hash demonstra integridade, não verdade.
8. A conformidade (`python3 prototype/conformance_v03.py`) tem de permanecer PASS.

## Governança
FOUNDER-LED: o fundador aprova mudanças de fundamentos matemáticos, contratos
públicos, remoção de funcionalidades, releases e merge na branch principal.

## Estrutura
- prototype/ — núcleo, VM, runtime, simulador, orquestrador, baterias
- docs/ — padrão executável, fases, scientific-kernel/ (Gen 1)
- docs/paper/ — preprint arXiv
- examples/ — programas .zeph reproduzíveis
