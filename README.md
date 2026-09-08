# Quick Filler — Transcrição de Documentos Trabalhistas

Aplicação web para transformar **cartões de ponto** e **holerites em PDF** em dados estruturados, revisáveis e exportáveis para planilhas.

> Este repositório documenta o projeto como uma aplicação em execução, e não como um exercício acadêmico.

## Projeto em execução

**Aplicação publicada:** https://quick-filler-cartao-de-ponto.onrender.com/

**Repositório:** https://github.com/GOVIAO/quick-filler

Fluxo principal:

```text
PDF → envio → processamento/OCR → revisão → correção → exportação
```

A arquitetura utiliza um único pipeline de processamento com dois extratores especializados: **cartão de ponto** e **holerite**.

## Objetivos

- Receber PDFs trabalhistas de diferentes layouts.
- Identificar quando o PDF possui texto pesquisável e quando precisa de OCR.
- Preservar o texto original (`*_raw`) e separar interpretação de normalização.
- Nunca inventar valores quando a leitura for incerta: usar `?` por caractere.
- Detectar datas e competências impossíveis antes da revisão.
- Permitir correção manual antes da exportação.
- Gerar `.xlsx`, `.csv` ou `.json` seguindo o contrato de dados.
- Manter o PDF visível durante a revisão.
- Exibir avisos derivados do próprio conteúdo, sem armazená-los no JSON.

## Tipos de documento

### Cartão de ponto

Cada página contém dias na ordem original. Cada dia possui a data impressa e uma sequência de batidas `IN`/`OUT`.

```json
{
  "pages": [
    {
      "page": 1,
      "days": [
        {
          "date_raw": "21/05/2019",
          "punches": [
            { "kind": "IN", "time_raw": "08:25", "time_hhmm": "08:25" },
            { "kind": "OUT", "time_raw": "18:25", "time_hhmm": "18:25" }
          ]
        }
      ]
    }
  ]
}
```

Avisos calculados: batidas ímpares, data não sequencial e presença de `?`.

### Holerite

Cada página possui competência, verbas da tabela principal e uma seção independente de bases/totais.

```json
{
  "pages": [
    {
      "page": 1,
      "year": "2020",
      "month": "01",
      "fields": [
        { "code": "0010", "label": "Salário Base", "reference": "220,00", "value": "2.389,77" }
      ],
      "bases": [
        { "label": "Base INSS", "value": "2.545,68" },
        { "label": "Valor Líquido", "value": "2.282,81" }
      ]
    }
  ]
}
```

A separação entre `fields` e `bases` é obrigatória. Avisos calculados: página vazia e mês não sequencial.

## Regras de precisão

1. **Não inventar valores.** Um caractere sem leitura segura recebe `?`.
2. **Não fabricar datas.** Datas impossíveis são erro de leitura.
3. **Preservar o original.** `date_raw` e `time_raw` mantêm o texto impresso.
4. **Normalizar somente com evidência suficiente.** `time_hhmm` representa a interpretação em 24 horas.
5. **Manter a ordem do documento.** Dias e verbas não são reordenados.
6. **Avisos são derivados.** São calculados na exibição/exportação.

## API

| Método | Endpoint | Finalidade |
|---|---|---|
| `POST` | `/api/transcricoes` | Envia PDF e cria processamento |
| `GET` | `/api/transcricoes/:id` | Consulta status e resultado |
| `PUT` | `/api/transcricoes/:id` | Salva correções da revisão |
| `GET` | `/api/transcricoes/:id/planilha` | Exporta a transcrição |
| `GET` | `/healthz` | Health check |

### Criar transcrição

`POST /api/transcricoes` com `multipart/form-data`:

- `arquivo`: PDF;
- `tipo`: `cartao-ponto` ou `holerite`.

Resposta:

```json
HTTP/1.1 202 Accepted
{ "id": "abc123" }
```

### Consultar processamento

```json
{
  "id": "abc123",
  "tipo": "cartao-ponto",
  "status": "concluido",
  "erro": null,
  "value": { "pages": [] }
}
```

Estados: `processando`, `concluido` e `erro`.

## Exportação

### Cartão de ponto

`Data | Entrada 1 | Saída 1 | Entrada 2 | Saída 2 | ...`

O número de pares é definido pela linha com maior quantidade de batidas.

### Holerite

`Pág. | Mês | Ano | <uma coluna por verba>`

As colunas são a união dos `label` encontrados, respeitando a ordem de primeira aparição.

## Destaques

| Situação | Preenchimento | Complemento |
|---|---|---|
| Batidas ímpares, página vazia ou `?` | `#FFF3CD` | — |
| Data ou mês não sequencial | `#F8D7DA` | Borda esquerda `#DC3545` |

Quando os dois alertas ocorrerem na mesma linha, o vermelho prevalece.

## Interface

O ciclo completo é: escolher PDF → escolher tipo → acompanhar processamento → visualizar PDF → revisar tabela editável → corrigir → baixar planilha.

## OCR e documentos escaneados

PDFs sem camada de texto precisam passar por OCR. A ferramenta e seus limites devem ser registrados em `SOLUCAO.md`. A estratégia é conservadora: em dúvida, sinalizar incerteza em vez de completar o valor por inferência.

## Segurança e privacidade

O sistema recebe documentos que podem conter nome, CPF, matrícula, salário e jornada. Por isso:

- limite de tamanho de upload;
- validação de PDF;
- tratamento controlado de arquivos inválidos/corrompidos;
- isolamento entre uploads simultâneos;
- nenhum conteúdo de documento ou PII em logs;
- política de retenção documentada em `SOLUCAO.md`;
- segredos somente por variáveis de ambiente.

## Execução local

```bash
docker compose up --build
```

O serviço deve disponibilizar `/healthz`.

## Testes e qualidade

A estratégia deve cobrir parsing de datas/horários, validação de datas e mês, regra de `?`, separação `fields`/`bases`, avisos, exportação, contrato HTTP, uploads inválidos/grandes e processamento concorrente.

## Documentação

- [`SOLUCAO.md`](SOLUCAO.md) — arquitetura, decisões, execução, limites, segurança e escopo.
- [`PROCESSO.md`](PROCESSO.md) — processo de desenvolvimento, uso de IA, decisões e pontos de confiança.
- [`docs/API.md`](docs/API.md) — contrato HTTP detalhado.
- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) — componentes e fluxo.
- [`docs/SEGURANCA.md`](docs/SEGURANCA.md) — upload, privacidade e retenção.

## Escopo e evolução

O projeto prioriza o ciclo completo **envio → processamento → revisão → exportação** para os dois tipos. Para layouts desconhecidos, a resposta correta é explicitar a incerteza ou informar que o layout não é suportado, nunca produzir dados com aparência de precisão.

Evoluções possíveis: rastreabilidade visual entre célula e PDF, detecção automática do tipo, ficha financeira anual, suporte incremental a layouts e observabilidade do processamento.

## Licença

Consulte [`LICENSE`](LICENSE).
