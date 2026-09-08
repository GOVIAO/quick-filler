# Processo de desenvolvimento — Quick Filler

## 1. Objetivo

Este documento registra como o Quick Filler foi organizado, quais ferramentas foram utilizadas e quais decisões exigem revisão humana. O foco é manter rastreabilidade do processo e deixar claro o que foi automatizado e o que precisa de validação.

## 2. Ferramentas utilizadas

- **ChatGPT (GPT-5.6 Luna):** apoio à análise do escopo, estruturação da documentação, revisão de contratos e organização do projeto.
- **GitHub:** versionamento, organização dos arquivos e histórico de commits.
- **Render:** publicação da aplicação e disponibilização da URL pública.
- **Docker / Docker Compose:** padronização da execução local e do ambiente da aplicação.
- **OCR:** leitura de páginas digitalizadas que não possuem camada textual útil.

As ferramentas de IA são auxiliares. A saída de documentos trabalhistas não deve ser aceita apenas porque um modelo produziu um valor plausível.

## 3. Como a solução foi construída

O desenvolvimento foi dividido em etapas:

1. entendimento do fluxo completo;
2. definição dos contratos JSON;
3. separação entre pipeline comum e extratores;
4. definição das regras de precisão;
5. definição dos avisos derivados;
6. definição do formato de exportação;
7. organização da documentação;
8. publicação e validação do fluxo web;
9. evolução dos testes e tratamento de casos de baixa confiança.

## 4. Onde a automação/IA pode errar

### Caso 1 — alteração de arquivo no GitHub

Na organização inicial da documentação, uma atualização do `README.md` foi enviada sem o SHA atual exigido pela operação de substituição de arquivo. O GitHub rejeitou a operação. O problema foi identificado pela resposta da API e corrigido buscando o SHA atual antes da nova atualização.

**Aprendizado:** operações destrutivas ou de substituição devem sempre partir do estado atual do repositório.

### Caso 2 — confundir documentação com evidência de implementação

Um risco identificado durante a organização do projeto é documentar uma capacidade apenas porque ela está no escopo desejado. Por isso, a documentação diferencia contrato, solução planejada e capacidade efetivamente verificada.

**Aprendizado:** não transformar requisito em afirmação de implementação sem evidência no código ou em teste.

### Caso 3 — OCR e valores plausíveis

Em documentos trabalhistas, um OCR pode produzir um número visualmente plausível mesmo quando um caractere está ilegível. A regra adotada é não “corrigir” por contexto. Quando não houver segurança suficiente, o caractere deve permanecer como `?` para revisão.

**Aprendizado:** plausibilidade não é evidência.

## 5. O que precisa ser reescrito/revisado manualmente

A camada de extração é a parte que não deve ser considerada pronta somente com geração automática de código ou documentação. Regras de layout, mapeamento de colunas, identificação de verbas e normalização de horários precisam ser confrontadas com os PDFs reais.

Também deve haver revisão manual dos casos com `?`, páginas vazias e alertas de sequência.

## 6. Decisões técnicas

### Decisão A — OCR local/abstraído vs. serviço externo

**Alternativas:** usar um OCR local, usar uma API externa ou combinar ambos.

**Escolha:** manter o OCR desacoplado do parser.

**Motivo:** o parser deve depender do texto/estrutura extraída, não do fornecedor de OCR. Isso facilita troca de motor, testes e evolução.

### Decisão B — salvar avisos no JSON vs. derivá-los

**Alternativas:** armazenar flags de alerta junto ao resultado ou calculá-las a partir do conteúdo.

**Escolha:** derivar os avisos.

**Motivo:** uma edição do usuário deve atualizar automaticamente o estado de validação, evitando dados duplicados e inconsistentes.

### Decisão C — uma aplicação para os dois documentos vs. duas aplicações

**Alternativas:** criar dois fluxos independentes ou compartilhar o pipeline.

**Escolha:** uma aplicação com pipeline comum e extratores especializados.

**Motivo:** upload, processamento, revisão e download são essencialmente iguais. O que muda é o parser e o formato de planilha.

## 7. O que quebra primeiro em produção

Os primeiros pontos de atenção são:

1. PDFs com layouts não previstos;
2. OCR em imagens de baixa qualidade;
3. arquivos muito grandes ou muitas páginas simultâneas;
4. aumento de tempo de processamento;
5. divergências entre um layout real e as regras do parser.

A mitigação prioritária é impedir resultados silenciosamente incorretos e expor a incerteza para revisão.

## 8. Onde a entrega não deve ser considerada confiável sem validação

Não é seguro assumir cobertura universal de layouts de cartão de ponto ou holerite. A solução deve ser considerada confiável apenas dentro dos layouts efetivamente testados.

Também não se deve considerar uma extração correta apenas porque a planilha abriu ou porque os números parecem coerentes. A validação precisa comparar o resultado com o PDF de origem.

## 9. Critério de qualidade

A prioridade do projeto é:

1. precisão;
2. preservação da informação original;
3. transparência da incerteza;
4. revisão humana;
5. facilidade de exportação;
6. desempenho.

Um resultado incompleto com `?` é preferível a um resultado inventado.

## 10. Registro de evolução

A documentação acompanha o projeto em execução. Novos layouts devem gerar testes de regressão antes de serem considerados suportados.

Toda mudança que altere o contrato JSON, a sequência de processamento ou a planilha deve atualizar a documentação correspondente.