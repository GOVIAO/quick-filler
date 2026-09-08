# SOLUCAO.md — Quick Filler

## Como rodar

```bash
docker compose up --build
```

A aplicação fica em `http://localhost:8000`.

## Arquitetura

Uma única aplicação FastAPI compartilha upload, processamento, revisão e exportação. O extrator é selecionado pelo campo `tipo`, sem duplicar o ciclo do produto.

- PDF com camada de texto: `pdfplumber`.
- Página sem texto: renderização + Tesseract OCR em português/inglês.
- Dados: memória do processo, sem banco externo.
- XLSX: `openpyxl`.
- CSV e JSON: exportação direta.

## Precisão e incerteza

A aplicação mantém `date_raw`, `time_raw` e `time_hhmm` no cartão de ponto. Quando uma leitura não pode ser determinada com segurança, a regra é preservar `?` em vez de inventar um valor.

Datas inválidas não são normalizadas. Horários fora de `00:00`–`23:59` recebem `?:??`.

## Avisos derivados

Os avisos são calculados a partir do JSON:

- cartão de ponto: batidas ímpares, leitura incerta e data não sequencial;
- holerite: página vazia, leitura incerta e mês não sequencial.

Sequencialidade não é armazenada como campo do contrato.

## Segurança e privacidade

- limite de upload: 15 MB;
- validação de assinatura `%PDF-` e leitura do PDF;
- conteúdo do documento não é escrito em logs pela aplicação;
- documentos ficam somente em memória e desaparecem quando o processo é reiniciado;
- não há autenticação nesta prova técnica, conforme escopo do desafio.

Em produção, eu adicionaria fila de jobs, isolamento por usuário/job, timeout, limite de CPU/memória, TTL explícito e armazenamento temporário criptografado.

## Escopo cortado

Não implementei rastreabilidade visual por coordenadas, detecção automática do tipo, ficha financeira anual e classificação avançada de layouts desconhecidos. Priorizei o ciclo completo para os dois tipos, conforme a orientação do desafio.

A edição da tabela cobre os campos principais usados na planilha. Bases do holerite continuam preservadas no JSON e no pipeline, mas não são colunas da planilha principal.

## O que quebra primeiro em produção

A extração heurística em layouts novos e OCR com baixa qualidade. O próximo investimento seria criar extratores por família de layout, testes com PDFs reais e uma fila assíncrona.

## Onde não confio totalmente

Em documentos escaneados com baixa resolução, tabelas complexas ou caracteres ambíguos. Nesses casos, o sistema deve preferir `?` e revisão humana a uma transcrição aparentemente correta.
