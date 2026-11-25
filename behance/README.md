# Behance Project Builder

Você me envia as imagens → eu analiso, escrevo os textos e gero tudo pronto para subir.

## O que sai em `pronto/`
- `imagens/01_*.jpg …` já na ordem, 1400 px de largura, ≤ 10 MB
- `capa_808x632.jpg`
- `projeto.txt` com título, descrição, tags, áreas e ferramentas para copiar e colar
- `preview.html` com a prévia do projeto
- `.zip` com tudo (opção `--zip`)

## Uso manual
```
pip install pillow
python3 behance/build_project.py minhas_imagens projeto.json -o pronto --zip
```
Exemplo de `projeto.json`: `behance/exemplo/projeto.json`.

## Observação
O upload em si é manual (o Behance não tem API pública de publicação). Basta arrastar a pasta `imagens/` na ordem e colar os textos de `projeto.txt`.
