# Fluxo: imagens → projeto Behance pronto

Quando o usuário enviar imagens (ou uma pasta) pedindo um projeto Behance:

1. **Olhar todas as imagens** e entender o trabalho (cliente, segmento, entregáveis, estilo, paleta).
2. **Definir a ordem narrativa**: capa/hero → contexto/logo → aplicações → detalhes → fechamento.
3. **Escrever os textos em pt-BR** (a menos que o usuário peça inglês, Behance é global: oferecer versão EN):
   - título curto e específico (cliente + tipo de trabalho)
   - descrição de 2–4 parágrafos: desafio, solução, resultado/entregáveis
   - até **10 tags**, até **3 áreas criativas**, ferramentas
   - não inventar dados (cliente, métricas, prêmios): se faltar, perguntar ou deixar placeholder `[PREENCHER]`
4. **Gravar `projeto.json`** (formato no topo de `build_project.py`) ao lado das imagens, em `behance/projetos/<slug>/`.
5. **Rodar**: `python3 behance/build_project.py behance/projetos/<slug>/originais behance/projetos/<slug>/projeto.json -o behance/projetos/<slug>/pronto --zip`
6. **Conferir** o `preview.html`/imagens geradas e os avisos do script; entregar ao usuário o `.zip` e o `projeto.txt`.

Specs usadas: largura 1400 px, JPG progressivo ≤ 10 MB, capa 808×632 px, até 10 tags e 3 áreas.
Imagens originais nunca são sobrescritas.
