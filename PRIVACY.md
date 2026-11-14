# Política de Privacidade e Tratamento de Dados — ZEPHIRUM / ZYQL

Versão 1.1 · Vigência: 2026-11-08 · Responsável: Reginaldo Pinezi Uhlmann · Serena Solutions · contato serena.aigronovatech@gmail.com

## 1. Princípio

O ZEPHIRUM foi construído para funcionar sem coletar dados pessoais. O padrão é
não coletar. Qualquer coleta futura exige revisão desta política antes de existir,
nunca depois.

## 2. O que o software faz localmente

1. Compila e executa programas na sua máquina ou no seu ambiente.
2. Gera recibos de execução assinados com chave do emissor.
3. Guarda esses recibos onde você mandar guardar.

Nada disso sai do seu ambiente por iniciativa do software.

## 3. O que um recibo contém

Um recibo v1 registra dados técnicos, não pessoais:

1. hash do programa, versão da linguagem, versão do compilador e versão da política;
2. identificador de execução, parâmetros (por exemplo, número de tiros) e horários;
3. hashes das evidências e o veredito com sua incerteza declarada;
4. assinatura Ed25519 e cadeia de recibos anteriores.

Um recibo não contém nome, e-mail, telefone, endereço, documento, localização, nem
o conteúdo dos seus dados de entrada: o compromisso de entrada é um hash, que não
permite reconstruir a entrada.

## 4. Telemetria

Não há telemetria. O software não envia estatísticas de uso, não registra
identificadores de dispositivo e não faz chamadas de rede por conta própria. Quando
uma execução usar hardware externo, a chamada é explícita, autorizada por política e
registrada no recibo.

## 5. Segredos e credenciais

1. Nenhuma chave, token ou senha é armazenada no repositório público.
2. Credenciais de execução ficam no seu cofre ou variáveis de ambiente locais.
3. Chaves públicas de verificação são publicadas de propósito: elas permitem verificar,
   não permitem assinar.

## 6. Papéis na proteção de dados (LGPD)

Ao usar o ZEPHIRUM nos seus próprios dados, você é o controlador e a Serena Solutions não trata
dados pessoais em seu nome. O software não cria conta, não pede cadastro e não exige identificação
para funcionar.

## 7. Direitos dos titulares

Como o software não coleta dados pessoais, não existe base de titulares a consultar, exportar ou
eliminar. Se você acredita que algum dado seu apareceu indevidamente em material do projeto,
escreva para o canal de contato do repositório e o caso será respondido por escrito.

## 8. Retenção

Recibos são seus e ficam onde você os guardar. O projeto não mantém cópia. A cadeia de recibos é
local ao ambiente de quem executou.

## 8-A. Cobrança: não existe

**Atualização de 08/11/2026.** A plataforma opera em **modo gratuito**. Não há plano pago, não há
checkout, não há assinatura e **não é solicitado nem armazenado e-mail, cartão ou qualquer dado de
pagamento**. Os endpoints de cobrança respondem com recusa explícita (`HTTP 410`) enquanto a
cobrança estiver desligada. Não há, portanto, tratamento de dados pessoais para fins de faturamento.

Se um dia houver cobrança, esta política será revisada e publicada **antes** da primeira transação,
declarando finalidade, base legal, prazo de retenção e canal do titular.

## 9. Limites declarados

1. Recibo válido prova origem e integridade do resultado, não a segurança da execução.
2. Um recibo publicado por você em repositório público passa a ser público; trate a
   decisão de publicar como sua.
3. Esta política cobre o software ZEPHIRUM/ZYQL. Ela não cobre sites de terceiros.

## 10. Mudanças

Alterações são versionadas no repositório oficial. A versão vigente está sempre em
`PRIVACY.md` na raiz. Mudança de escopo de coleta exige nota de revisão e nova versão.
