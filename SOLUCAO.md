# Solução técnica — Quick Filler

## 1. Visão geral

O Quick Filler é uma aplicação web de processamento de documentos trabalhistas. O objetivo é transformar PDFs de **cartão de ponto** e **holerite** em uma transcrição estruturada, permitir revisão humana e gerar uma planilha final.

O projeto é organizado como um único pipeline com dois extratores especializados, evitando duplicação entre os tipos de documento.

```text
Upload PDF
   ↓
Validação
   ↓
Criação da transcrição
   ↓
Processamento assíncrono
   ↓
Extração de texto / OCR
   ↓
Parser do tipo de documento
   ↓
JSON canônico
   ↓
Revisão humana
   ↓
PUT das correções
   ↓
Exportação XLSX / CSV / JSON
```

## 2. Princípios

A decisão central é tratar a transcrição como um dado auditável, não como uma tentativa de reconstruir o que o documento provavelmente queria dizer.

- Não inventar valores.
- Usar `?` quando um caractere não puder ser identificado com segurança.
- Preservar campos `*_raw`.
- Não produzir datas impossíveis.
- Manter a ordem original do documento.
- Calcular avisos a partir dos dados, sem adicionar flags ao contrato.
- Permitir correção humana antes do download.

## 3. OCR

O pipeline primeiro tenta aproveitar a camada textual do PDF. Quando uma página não possui texto útil, ela deve ser renderizada como imagem e encaminhada para OCR.

A escolha do mecanismo de OCR é deliberadamente desacoplada dos parsers. Isso permite trocar o motor sem modificar o contrato de saída.

Em documentos difíceis, o comportamento esperado é conservador: baixa confiança não deve virar um valor aparentemente correto. O resultado deve preservar a incerteza com `?` para posterior revisão.

## 4. Cartão de ponto

O extrator identifica as linhas correspondentes aos dias e mantém a ordem de apresentação.

Cada dia produz:

- `date_raw`;
- `punches[]`;
- `kind` alternando `IN` e `OUT` conforme a posição das batidas;
- `time_raw`;
- `time_hhmm`.

A quantidade de batidas é preservada mesmo quando é ímpar. Não se cria uma batida inexistente para completar o par.

### Avisos

- número ímpar de batidas;
- data não sequencial;
- presença de `?`.

A sequência é avaliada na ordem do documento, e não por uma ordenação posterior.

## 5. Holerite

O parser separa explicitamente duas estruturas:

### `fields`

Somente as verbas da tabela principal. Cada item contém código, descrição, referência e valor.

### `bases`

Somente bases e totais da seção separada, como Base INSS, Base IR, FGTS, Total Vencimentos e Valor Líquido.

Essa separação evita transformar totais em verbas e é essencial para a exportação matricial.

### Avisos

- página vazia;
- mês não sequencial.

Competências ilegíveis não quebram a cadeia: as próximas competências legíveis são comparadas entre si.

## 6. Exportação

### Cartão de ponto

A primeira coluna é `Data`. Depois vêm pares `Entrada N` e `Saída N`. O número de pares é determinado pelo maior número de batidas encontrado.

### Holerite

As três primeiras colunas são `Pág.`, `Mês` e `Ano`. As demais são construídas pela união dos `label` de `fields`, preservando a primeira aparição.

Os valores monetários continuam como strings brasileiras, por exemplo `2.389,77`.

As linhas com problemas recebem os destaques definidos pelo projeto. Quando há alerta amarelo e vermelho na mesma linha, o vermelho prevalece.

## 7. API

A API mantém o contrato literal:

- `POST /api/transcricoes` recebe `arquivo` e `tipo` e retorna `202` com `id`;
- `GET /api/transcricoes/:id` acompanha `processando`, `concluido` ou `erro`;
- `PUT /api/transcricoes/:id` substitui o `value` pelas correções da revisão;
- `GET /api/transcricoes/:id/planilha` exporta `xlsx`, `csv` ou `json`;
- `GET /healthz` verifica disponibilidade.

O processamento é assíncrono para que o upload não fique preso a uma operação longa de OCR.

## 8. Interface

A interface acompanha o estado do processamento e, quando concluído, apresenta o PDF e a tabela de revisão simultaneamente.

A tabela é editável. Os problemas são calculados novamente depois das alterações, evitando que uma correção continue marcada por um aviso que já não existe.

O download sempre representa o estado salvo da transcrição.

## 9. Segurança

O endpoint de upload é público e pode receber dados pessoais. As proteções previstas são:

- limite de tamanho;
- validação do tipo real do arquivo;
- rejeição controlada de PDF inválido/corrompido;
- isolamento por identificador de transcrição;
- tratamento de uploads simultâneos;
- ausência de conteúdo documental e PII nos logs;
- configuração por variáveis de ambiente;
- nenhuma credencial versionada.

## 10. Retenção

A política operacional recomendada é manter os arquivos somente pelo tempo necessário ao processamento e revisão. Em ambiente de demonstração, os dados devem ser tratados como temporários e removidos após o período definido pela aplicação.

Nenhum documento de produção deve ser mantido indefinidamente sem uma política explícita, controle de acesso e justificativa operacional.

## 11. Docker

A execução oficial é:

```bash
docker compose up --build
```

O `docker-compose.yml` é a referência para subir o ambiente completo. Variáveis específicas do ambiente devem ser fornecidas externamente, com `.env.example` servindo apenas como documentação.

## 12. Testes

A suíte deve validar principalmente:

- datas válidas e impossíveis;
- horários e normalização `HH:MM`;
- preservação de `*_raw`;
- uso de `?` por caractere;
- sequência de datas;
- sequência de competências;
- separação entre `fields` e `bases`;
- página vazia;
- geração das colunas das planilhas;
- contrato HTTP;
- upload inválido e acima do limite;
- concorrência.

## 13. O que fica fora da primeira versão

Para manter o ciclo completo funcional, funcionalidades de maior profundidade podem ser evoluídas posteriormente:

- rastreabilidade visual célula → coordenada no PDF;
- detecção automática do tipo de documento;
- ficha financeira anual;
- suporte amplo a layouts desconhecidos;
- observabilidade avançada do pipeline.

A escolha é preservar o fluxo ponta a ponta dos dois tipos, em vez de concentrar todo o esforço em um único extrator.

## 14. Limitações conhecidas

OCR é a principal fonte de incerteza. Layouts novos podem exigir regras específicas. A revisão humana continua sendo parte importante do fluxo porque o domínio prioriza não produzir um número incorreto com aparência de precisão.

Quando o sistema não tiver evidência suficiente para interpretar um campo, a saída correta é sinalizar a incerteza.

## 15. Evolução

A arquitetura permite adicionar novos parsers e estratégias de OCR sem mudar o contrato público. O próximo ganho técnico relevante é rastrear coordenadas de origem desde o OCR até cada célula da tabela, permitindo auditoria visual direta.