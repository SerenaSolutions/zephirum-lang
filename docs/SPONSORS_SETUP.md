# GitHub Sponsors + doações + Marketplace — guia de ativação (2026-10-21)

## A. GitHub Sponsors (doações recorrentes)
VIA: github.com/sponsors (web, 10 min, exige conta do dono):
1. Entrar logado como SerenaSolutions em https://github.com/sponsors
2. "Get started" → espera de aprovação da GitHub (normalmente dias)
3. Conectar o Stripe (pagamentos e repasses da GitHub) — o repasse do Stripe
   vai pra CONTA BANCÁRIA, não via Pix. Brasil é país suportado pelo Stripe.
4. Tiers sugeridos (rascunho): R$10 "Apoiador" | R$50 "Patrono da ciência"
   | R$200 "Sócio do laboratório" (limites da casa, decidir com contador)
5. O botão Sponsor do repositório já aponta pra SerenaSolutions
   (.github/FUNDING.yml, commitado).

## B. Chave Pix (doação direta BR)
- A GitHub NÃO aceita Pix — Pix é canal DIRETO, mostrado por nós:
  README do repo + página do perfil espelho (profile/index.html) + posts.
- A chave informada pelo dono entra em: FUNDING.yml (comentário),
  README (seção Apoie) e página espelho. Pix é dado público por natureza.

## C. Marketplace
1. Action gratuita (VISIBILIDADE): action.yml do zq-gate já criado na raiz.
   Publicar: criar release v1 do action marcando "Publish to Marketplace"
   no form do release (1 clique do dono na web). Instalação: uses: SerenaSolutions/zephirum-lang/.github/action.yml? Não — uses: SerenaSolutions/zephirum-lang@v1.
2. App pago no Marketplace (RENDA): exige GitHub App + Stripe + revisão da
   GitHub. SÓ após o conserto do CNAE (abaixo) para faturar CNPJ→CNPJ.

## D. O CONCERTO DO CNPJ (a raiz do "que bosta")
O CNAE do CNPJ atual não abrange venda de software — ISSO SE MUDA:
1. Portal Redesim (redesim.gov.br) → alteração de CNAE da empresa
2. CNAEs de software: 6201-5/01 (desenvolvimento de software),
   6202-3/00 (consultoria em TI), 6209-1/00 (suporte), 6311-9/99 (portais)
3. Custo: taxa da Junta (baixa); prazo: dias
4. ATENÇÃO MEI: se o CNPJ for MEI, alguns CNAEs de software têm restrições
   de atividades permitidas — conferir com contador; se necessário,
   desenquadrar pra ME (EPP) abre o leque
5. RECOMENDAÇÃO DA CASA: contador confere enquadramento e impostos
   (doação vs receita de software têm naturezas diferentes)
Enquanto o CNAE não muda: doação (Sponsors/Pix) é o canal honesto de entrada.
