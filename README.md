# Quick Filler — Desafio Técnico

Aplicação web para transcrição de cartões de ponto e holerites em PDFs para planilhas estruturadas.

## Executar

```bash
docker compose up --build
```

Abra `http://localhost:8000`.

## Desenvolvimento local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload
```

## Fluxo

1. Enviar PDF e escolher o tipo.
2. Processar texto ou OCR quando a página não tiver camada de texto.
3. Conferir PDF lado a lado com a transcrição editável.
4. Corrigir campos e salvar.
5. Baixar XLSX, CSV ou JSON.

## Estrutura

- `app/main.py`: API, extratores, avisos e exportadores.
- `app/templates/index.html`: interface.
- `app/static/`: CSS e JavaScript.
- `tests/`: testes automatizados.
- `SOLUCAO.md`: decisões, operação e limitações.
- `PROCESSO.md`: processo de desenvolvimento com IA.
