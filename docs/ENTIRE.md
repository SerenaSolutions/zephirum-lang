# Espelhamento para o Entire (forge Git para colaboração humano-agente)

## O que é
Entire (entire.com / entire.io) é uma forge Git criada por **Thomas Dohmke**, ex-CEO do GitHub,
com US$ 60 mi de seed. Não é brasileira: o que existe de Brasil é uma **região espelho em São
Paulo**, junto de Frankfurt, Mumbai e Sydney. O produto guarda a intenção junto do código
(sessões de agente, "Trails" no lugar do PR, evals no centro da revisão).

Por que faz sentido para nós: a tese deles é *preservar a decisão junto do artefato*. É
exatamente o que o recibo selado do ZYQL faz. Encaixe técnico, não vitrine.

## Estado verificado (03/11/2026)
- `https://entire.com/et/ravi-quantinum/-/repositories` → redireciona para **Login**.
  Ou seja: o namespace existe como rota autenticada, não é página pública.
- Nenhuma credencial do Entire está no ambiente do sandbox (`ENTIRE_TOKEN` ausente).

## Como espelhar (script pronto)
```bash
./scripts/mirror_to_entire.sh --dry-run     # imprime o plano, não envia nada
ENTIRE_TOKEN=... ./scripts/mirror_to_entire.sh
```
O script lista os 32 repositórios da conta e empurra cada um para
`https://entire.com/et/<namespace>/<repo>.git`. Token vai por header HTTP, nunca na URL, e
falha de um repo não esconde as demais: o resumo final conta espelhados e falhas.

## O que falta para funcionar
1. Criar token de acesso no Entire (painel da conta).
2. Salvar na plataforma como segredo **ENTIRE_TOKEN** (nunca colar no chat).
3. Confirmar o namespace correto — o link do dono diz `ravi-quantinum`, e vale conferir se é
   esse mesmo (o nome do agente é "Ravi Quantuno", sem o "i" depois do n).

## O que NÃO fazer
1. Não tratar o Entire como substituto do GitHub: Qiskit Ecosystem, conda-forge e os índices
   awesome vivem no GitHub. Forge nova não move esses ativos.
2. Não publicar em plataforma nova antes do espelhamento funcionar: perfil com repositório
   vazio queima a primeira impressão.
