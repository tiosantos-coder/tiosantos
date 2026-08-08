#!/usr/bin/env python3
"""
Gerador de páginas estáticas individuais para cada microtexto do textos.json.

Uso:
    python3 generate_textos.py

Lê textos.json na mesma pasta e gera um arquivo /textos/{id}.html por item,
todos seguindo exatamente o mesmo template (mesma tipografia, cores e
metadados padronizados do site). Também atualiza o index.html: corrige os
metadados do <head> e troca as funções de compartilhamento (shareWAMicro,
copiarLink) para apontarem para a URL própria de cada texto em vez da
âncora (#id), garantindo preview correto no WhatsApp.

Rodar de novo sempre que textos.json mudar (novo microtexto adicionado).
"""

import json
import re
import html
from pathlib import Path

BASE_DIR = Path(__file__).parent
SITE_URL = "https://tiosantos.pages.dev"

# ---------------------------------------------------------------------------
# Template de cada página individual de microtexto (/textos/{id}.html)
# ---------------------------------------------------------------------------

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo_esc} — Tio Santos</title>
  <meta name="description" content="{descricao_esc}">
  <link rel="canonical" href="{url_pagina}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Inter:wght@400;500&display=swap" rel="stylesheet">

  <!-- Open Graph -->
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{url_pagina}" />
  <meta property="og:title" content="{titulo_esc} — Tio Santos" />
  <meta property="og:description" content="{descricao_esc}" />
  <meta property="og:image" content="{imagem_card}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:locale" content="pt_BR" />
  <meta property="article:published_time" content="{data_iso}" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{titulo_esc} — Tio Santos" />
  <meta name="twitter:description" content="{descricao_esc}" />
  <meta name="twitter:image" content="{imagem_card}" />

  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --white: #ffffff;
      --off-white: #f7f5f0;
      --mid-gray: #999;
      --dark-gray: #444;
      --text: #1a1a1a;
      --accent: #2c5f8a;
      --border: #e0ddd8;
      --terracota: #b5451b;
      --serif: 'Cormorant Garamond', Georgia, serif;
      --sans: 'Inter', system-ui, sans-serif;
      --max: 680px;
    }}
    body {{
      font-family: var(--sans);
      background: var(--white);
      color: var(--text);
      line-height: 1.6;
    }}
    .voltar {{
      display: block;
      max-width: var(--max);
      margin: 0 auto;
      padding: 1.5rem 2rem 0;
      font-size: 0.78rem;
      letter-spacing: 0.05em;
      color: var(--mid-gray);
      text-decoration: none;
    }}
    .voltar:hover {{ color: var(--text); }}
    main {{
      max-width: var(--max);
      margin: 0 auto;
      padding: 1.5rem 2rem 3rem;
    }}
    .micro-tipo {{
      font-size: 0.7rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--terracota);
      margin-bottom: 0.5rem;
      font-family: var(--sans);
    }}
    .micro-data {{
      font-size: 0.7rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--mid-gray);
      margin-bottom: 1.2rem;
      font-family: var(--sans);
    }}
    h1 {{
      font-family: var(--serif);
      font-weight: 500;
      font-size: clamp(1.6rem, 5vw, 2.1rem);
      line-height: 1.25;
      margin-bottom: 1rem;
      border-left: 3px solid var(--terracota);
      padding-left: 1rem;
    }}
    .micro-texto p {{
      font-family: var(--serif);
      font-size: 1.15rem;
      line-height: 1.85;
      color: var(--dark-gray);
      margin-bottom: 1.1rem;
    }}
    .assinatura {{
      margin-top: 1.5rem;
      font-family: var(--serif);
      font-style: italic;
      color: var(--mid-gray);
    }}
    .share-buttons {{
      display: flex;
      gap: 0.6rem;
      flex-wrap: wrap;
      margin-top: 2rem;
      padding-top: 1.2rem;
      border-top: 1px solid var(--border);
    }}
    .share-btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-family: var(--sans);
      font-weight: 500;
      text-decoration: none;
      color: #fff;
      background: #25D366;
    }}
    footer {{
      background: var(--off-white);
      border-top: 1px solid var(--border);
      padding: 1.5rem 2rem;
      text-align: center;
      font-size: 0.78rem;
      color: var(--mid-gray);
      font-family: var(--sans);
    }}
    footer a {{ color: var(--accent); text-decoration: none; }}
    .micro-imagem {{
      width: 100%;
      max-width: var(--max);
      margin: 0 auto 1.5rem;
      display: block;
      border-radius: 4px;
    }}
  </style>
</head>
<body>

  <a class="voltar" href="{site_url}/">&larr; tiosantos</a>

  <main>
    <p class="micro-tipo">{tipo_esc}</p>
    <p class="micro-data">{data_fmt}</p>
    <h1>{titulo_esc}</h1>
{imagem_html}
    <div class="micro-texto">
{paragrafos}
    </div>
    <p class="assinatura">★ tiosantos</p>

    <div class="share-buttons">
      <a class="share-btn" target="_blank" rel="noopener"
         href="https://wa.me/?text={whatsapp_texto}">
        Compartilhar no WhatsApp
      </a>
    </div>
  </main>

  <footer>
    <p>Valdemir de Oliveira Gomes — Tio Santos · <a href="{site_url}/">ver todos os textos</a></p>
  </footer>
</body>
</html>
"""


def formatar_data(data_iso: str) -> str:
    """Converte '2026-07-25' em '25 de julho de 2026'."""
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    ano, mes, dia = data_iso.split("-")
    return f"{int(dia):02d} de {meses[int(mes) - 1]} de {ano}"


def montar_paragrafos(texto: str) -> str:
    """Quebra o texto em parágrafos <p>, separando por linha em branco dupla."""
    partes = [p.strip() for p in texto.split("\n\n") if p.strip()]
    linhas = []
    for p in partes:
        p_html = html.escape(p).replace("\n", "<br>")
        linhas.append(f"      <p>{p_html}</p>")
    return "\n".join(linhas)


def gerar_pagina(item: dict) -> str:
    titulo_esc = html.escape(item["titulo"])
    descricao_esc = html.escape(item["resumo"])
    tipo_esc = html.escape(item["tipo"])
    data_fmt = formatar_data(item["data"])
    url_pagina = f"{SITE_URL}/textos/{item['id']}.html"

    imagem_item = item.get("imagem")  # caminho relativo opcional, ex: "/textos/img/arquivo.jpg"
    if imagem_item:
        imagem_card = f"{SITE_URL}{imagem_item}"
        alt_esc = html.escape(item.get("imagem_alt", item["titulo"]))
        imagem_html = f'    <img class="micro-imagem" src="{imagem_item}" alt="{alt_esc}">'
    else:
        imagem_card = f"{SITE_URL}/tiosantos.jpg"  # imagem padrão até haver card individual
        imagem_html = ""
    whatsapp_texto = html.escape(
        f"{item['resumo']}\n\nLeia o texto completo em {url_pagina}",
        quote=True
    ).replace("&amp;", "%26").replace("\n", "%0A").replace(" ", "%20")

    # encode simples e seguro para query string (evita depender de urllib aqui)
    import urllib.parse
    whatsapp_texto = urllib.parse.quote(
        f"{item['resumo']}\n\nLeia o texto completo em {url_pagina}"
    )

    return PAGE_TEMPLATE.format(
        titulo_esc=titulo_esc,
        descricao_esc=descricao_esc,
        tipo_esc=tipo_esc,
        data_fmt=data_fmt,
        data_iso=item["data"],
        url_pagina=url_pagina,
        imagem_card=imagem_card,
        imagem_html=imagem_html,
        paragrafos=montar_paragrafos(item["texto"]),
        site_url=SITE_URL,
        whatsapp_texto=whatsapp_texto,
    )


def atualizar_index(index_content: str) -> str:
    """Corrige metadados do <head> e as funções de compartilhamento do index.html."""

    # 1) Corrige <title>
    index_content = re.sub(
        r"<title>.*?</title>",
        "<title>Valdemir de Oliveira Gomes — Tio Santos | Gestor Cultural, Poeta e Cronista</title>",
        index_content, count=1
    )

    # 2) Corrige meta description
    index_content = re.sub(
        r'<meta name="description" content=".*?">',
        '<meta name="description" content="Gestor cultural com mais de 35 anos de atuação em Diadema/SP. '
        'Parecerista credenciado, poeta, compositor e cronista. Textos, música e trajetória de Valdemir de Oliveira Gomes.">',
        index_content, count=1
    )

    # 3) Corrige og:title / twitter:title (de "tiosantos" para nome completo)
    index_content = index_content.replace(
        '<meta property="og:title" content="tiosantos" />',
        '<meta property="og:title" content="Valdemir de Oliveira Gomes — Tio Santos" />'
    )
    index_content = index_content.replace(
        '<meta name="twitter:title" content="tiosantos" />',
        '<meta name="twitter:title" content="Valdemir de Oliveira Gomes — Tio Santos" />'
    )

    # 4) og:type de "website" para "profile"
    index_content = index_content.replace(
        '<meta property="og:type" content="website" />',
        '<meta property="og:type" content="profile" />'
    )

    # 5) Adiciona og:locale e canonical logo depois do og:url, se ainda não existir
    #    (procura pelo domínio ANTIGO fixo, que é o que existe no arquivo original)
    if 'og:locale' not in index_content:
        index_content = index_content.replace(
            '<meta property="og:url" content="https://tiosantos.pages.dev/" />',
            '<meta property="og:url" content="https://tiosantos.pages.dev/" />\n'
            '  <meta property="og:locale" content="pt_BR" />'
        )
    if 'rel="canonical"' not in index_content:
        index_content = index_content.replace(
            "</title>",
            "</title>\n  <link rel=\"canonical\" href=\"https://tiosantos.pages.dev/\">",
            1
        )

    # 6) Ajusta shareWAMicro para linkar para /textos/{id}.html em vez da âncora
    #    (o texto procurado é sempre o do arquivo ORIGINAL, com domínio antigo)
    index_content = index_content.replace(
        """function shareWAMicro(resumo, ancId) {
      const link = 'https://tiosantos.pages.dev/#' + ancId;
      const texto = resumo + '\\n\\nLeia o texto completo em ' + link;
      const url = 'https://wa.me/?text=' + encodeURIComponent(texto);
      window.open(url, '_blank');
    }""",
        """function shareWAMicro(resumo, ancId) {
      const link = 'https://tiosantos.pages.dev/textos/' + ancId + '.html';
      const texto = resumo + '\\n\\nLeia o texto completo em ' + link;
      const url = 'https://wa.me/?text=' + encodeURIComponent(texto);
      window.open(url, '_blank');
    }"""
    )

    # 7) Ajusta copiarLink da mesma forma
    index_content = index_content.replace(
        """function copiarLink(ancId) {
      const link = 'https://tiosantos.pages.dev/#' + ancId;
      navigator.clipboard.writeText(link).then(() => {
        alert('Link copiado: ' + link);
      });
    }""",
        """function copiarLink(ancId) {
      const link = 'https://tiosantos.pages.dev/textos/' + ancId + '.html';
      navigator.clipboard.writeText(link).then(() => {
        alert('Link copiado: ' + link);
      });
    }"""
    )

    # 8) Troca final e global: qualquer ocorrência restante do domínio antigo
    #    fixo (https://tiosantos.pages.dev) — og:url, og:image, twitter:image,
    #    variável _siteUrl, link direto de música/crônica, e qualquer outro
    #    lugar não coberto pelos passos acima — é substituída pelo SITE_URL
    #    configurado no topo deste arquivo. Isso é seguro: o domínio antigo
    #    só aparece em URLs completas do site, nunca em caminhos relativos
    #    de arquivo (mp3, jpg, pdf etc.), então não há risco de sobrescrever
    #    referência errada.
    index_content = index_content.replace("https://tiosantos.pages.dev", SITE_URL)

    return index_content


def main():
    with open(BASE_DIR / "textos.json", encoding="utf-8") as f:
        data = json.load(f)

    out_dir = BASE_DIR / "textos"
    out_dir.mkdir(exist_ok=True)

    gerados = []
    for item in data["microtextos"]:
        pagina_html = gerar_pagina(item)
        out_path = out_dir / f"{item['id']}.html"
        out_path.write_text(pagina_html, encoding="utf-8")
        gerados.append(str(out_path))
        print(f"Gerado: textos/{item['id']}.html")

    with open(BASE_DIR / "index.html", encoding="utf-8") as f:
        index_content = f.read()
    index_atualizado = atualizar_index(index_content)
    (BASE_DIR / "index.html").write_text(index_atualizado, encoding="utf-8")
    print("Atualizado: index.html (metadados + funções de compartilhamento)")

    print(f"\nTotal de páginas geradas: {len(gerados)}")


if __name__ == "__main__":
    main()
