# PROCESSO.md

## Ferramentas usadas

- Assistente de IA: estrutura inicial, implementação e revisão do contrato.
- Python/FastAPI: API e servidor web.
- pdfplumber/pypdf: leitura e validação de PDFs.
- Tesseract + Pillow: OCR de páginas escaneadas.
- openpyxl: XLSX.
- Docker Compose: execução reproduzível.
- pytest: testes automatizados.

## Onde o agente errou ou pegou caminho errado

1. Uma versão inicial tratava a interface de edição como protótipo e não persistia as células. Isso foi corrigido para sincronizar a tabela com o JSON e usar `PUT`.
2. Uma versão inicial devolvia XLSX quando o formato solicitado era CSV. O exportador foi separado e agora respeita `xlsx`, `csv` e `json`.
3. A primeira heurística de holerite era permissiva demais. A solução atual separa `fields` de `bases` por rótulos e documenta que layouts novos precisam de revisão.

## O que foi reescrito à mão e por quê

O contrato HTTP, regras de incerteza, avisos, formato das planilhas e política de retenção foram alinhados ao enunciado antes de adicionar conveniências de implementação.

## Três decisões com mais de uma resposta razoável

1. **OCR local ou nuvem:** escolhi OCR local para evitar enviar PII de documentos trabalhistas a terceiros.
2. **Processamento síncrono ou fila:** mantive processamento síncrono nesta prova para reduzir infraestrutura; em produção usaria fila.
3. **Memória ou banco:** escolhi memória para evitar persistência desnecessária de dados sensíveis durante o desafio.

## O que quebra primeiro em produção

Layouts desconhecidos, OCR ruim e PDFs grandes/concurrentes.

## Onde não confio no resultado

Na interpretação de caracteres ambíguos e na associação de colunas de layouts que nunca foram vistos. O sistema expõe incertezas para revisão em vez de ocultá-las.
