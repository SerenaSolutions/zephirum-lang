# Página de estado verificável

Publicada em https://zyql-estado.vercel.app (projeto Vercel `zyql-estado`, mesmo
`vercel.json` da raiz: `outputDirectory: "site"`, sem build).

Todo número da página vem de recibo. Nada é digitado à mão.

## Fontes

- `dados/recibo_hardware_20261114T164802.json` — execução em QPU (`ibm_fez`), Deutsch-Jozsa
  constante e balanceado, 4096 disparos, com bloco de calibração e job ids.
- `dados/envelope_largura.json` — GHZ de 10 a 100 qubits, 1024 disparos, medindo a
  fração de medidas em que todos os qubits concordam.

## Regenerar

```bash
python3 site/estado/gerar.py
```

O gerador reescreve `index.html` e recalcula o selo SHA3-256 sobre os dois arquivos de
origem (nome + conteúdo, nesta ordem). Quem tiver o repositório confere o selo sem
depender do autor.

## Publicar

O site é estático e versionado; o deploy sai do diretório do projeto:

```bash
vercel deploy --prod
```

O vínculo com a conta fica em `.vercel/`, que já está no `.gitignore`. Token nunca
entra no repositório.

## O que a página não afirma

Vantagem clássica, endosso de fornecedor, certificação. E declara o próprio limite:
acima de 30 qubits não há sinal utilizável, e o envelope de disparos que define quando
o gate começa a decidir ainda não foi medido.
