# Entrar no Entire — passo a passo real (verificado na documentação oficial)

## Por que a tela de repositórios aparece vazia

A documentação do Entire é explícita: *antes de criar qualquer mirror, o **Entire GitHub App**
precisa ter acesso ao repositório.* Sem o app instalado, não existe o que listar. Não é bug da
interface nem falta de campo: é ordem de operações.

## Dois modelos diferentes (não confundir)

1. **Mirror (espelho)**: o repositório continua tendo o GitHub como origem, e o Entire guarda
   uma cópia sincronizada numa ou mais regiões. Serve para clone e fetch rápidos perto de onde os
   agentes rodam. *Não move, não apaga e não substitui o GitHub.*
2. **Hospedagem nativa no Entire**: o repositório nasce no Entire. É o que dá branches nativas
   (`/guides/repositories/entire-native-branches`), inclusive para seguir trabalhando se o GitHub
   cair.

Para o nosso caso — manter o GitHub como fonte de verdade (an industry-standard quantum SDK, conda-forge, índices) e ter
cópia versionada no Entire — o modelo certo é o **mirror**.

## Passo a passo (mirror)

1. Instalar o **Entire GitHub App** na conta `SerenaSolutions`, escolhendo os repositórios
   (pelo menos `zephirum-lang` e `zq-ir`). Esse é o passo que faltava.
2. Abrir `entire.com` → **Repositories** → **Mirrors** → escolher o repositório e a região.
   Regiões disponíveis hoje: Ohio (EUA), Frankfurt (UE), Mumbai (Índia), Sydney (Austrália),
   Singapura e **São Paulo**.
3. Alternativa por terminal: instalar o CLI do Entire
   (`github.com/entireio/cli`) e usar `entire repo remote add` — ou `entire repo clone`.
   Sem terminal, um mirror de GitHub cai em `aws-us-east-2.entire.io` por padrão; em script,
   passar `--cluster` ou `--nearest`.

## O que muda e o que não muda

| muda | não muda |
|---|---|
| você ganha um remote `entire://` | o GitHub continua sendo a origem |
| clone/fetch mais rápidos na região | histórico Git não é reescrito |
| lista de acesso sincronizada do GitHub a cada hora | regras e autenticação do GitHub seguem valendo |
| | não exige que todo dev troque de remote |

Quem tem *read* no GitHub clona; quem tem *write* pode empurrar. Ou seja: acesso é herdado do
GitHub, não configurado à mão.

## Limite declarado

Mirrors **não suportam Git LFS** hoje. Se um repo usar LFS, o checkout pelo remote `entire://`
falha; a saída é manter o LFS apontado para o GitHub. Nossos repositórios não usam LFS, então
isso não nos atinge.

## Correção de rota neste documento

A versão anterior deste arquivo descrevia um push direto para
`https://entire.com/et/<namespace>/<repo>.git`. *Estava errado*: esse caminho não é o mecanismo
documentado. O oficial é GitHub App + mirror placement (ou CLI), e o remote resultante é
`entire://`. O script `scripts/mirror_to_entire.sh` fica como está para o cenário nativo
(push direto em repo criado no Entire), mas o caminho recomendado para nós é o mirror.
