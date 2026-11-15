#!/usr/bin/env python3
"""Gera o site tiosantos a partir de textos.json, obra.json e sobre.json.

Uso (na pasta do site):  python build.py

Escreve: index.html, microtextos.html, obra.html, sobre.html,
textos/<id>.html (um por microtexto), obra/<id>.html (um por peça) e sitemap.xml.
Só usa a biblioteca padrão do Python.

Para publicar um microtexto novo: acrescente a entrada em textos.json
(id, data AAAA-MM-DD, titulo, tipo, resumo, texto; opcionais: imagem, card,
video, destaque) e rode este arquivo de novo.
"""
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent
SITE = "https://tiosantos.pages.dev"
MARCA = "tiosantos"
AUTOR = "Valdemir de Oliveira Gomes"
DESCRICAO = "Poeta, compositor e cronista. Textos, músicas e reflexões sobre cultura, memória e identidade."
CARD_PADRAO = "/tiosantos.jpg"
SECAO_OBRA = "Textos, músicas e crônicas"
FORMSPREE = "https://formspree.io/f/xeeyekeb"
FONTES = ("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600"
          "&family=IBM+Plex+Mono:wght@400;500&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;1,7..72,400&display=swap")
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
GRUPOS = [("Músicas", ["Música"]),
          ("Poemas", ["Poema", "Poema manuscrito"]),
          ("Prosa poética", ["Prosa poética"]),
          ("Crônicas e ensaios", ["Crônica", "Apresentação", "Ensaio"]),
          ("Entrevistas", ["Entrevista"])]

SETA = ('<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg>')
IC_MENU = ('<svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
           'stroke-width="2" stroke-linecap="round"><path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/></svg>')
IC_ZAP = ('<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
          'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 20.5l1.7-5.2A8.5 8.5 0 1 1 21 11.5z"/></svg>')
IC_ENVIAR = ('<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 15V4"/><path d="M8 8l4-4 4 4"/><path d="M5 13v6h14v-6"/></svg>')
IC_LINK = ('<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
           'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/>'
           '<path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/></svg>')


def e(s):
    return html.escape(str(s), quote=True)


def ler(nome):
    return json.loads((RAIZ / nome).read_text(encoding="utf-8"))


def data_curta(iso):
    a, m, d = iso.split("-")
    return f"{d} {MESES[int(m) - 1][:3]} {a}"


def data_longa(iso):
    a, m, d = iso.split("-")
    return f"{int(d)} de {MESES[int(m) - 1]} de {a}"


def minutos(texto):
    return max(1, round(len(re.findall(r"\w+", texto)) / 200))


def sem_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def cortar(s, n=155):
    s = sem_tags(s)
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def url(caminho):
    """Endereço público: sem .html e sem index."""
    caminho = re.sub(r"index\.html$", "", caminho)
    return SITE + "/" + re.sub(r"\.html$", "", caminho)


def absoluto(caminho):
    return caminho if caminho.startswith("http") else SITE + caminho


# --------------------------------------------------------------- moldura
def pagina(caminho, titulo, descricao, corpo, atual="", imagem=CARD_PADRAO, tipo="website",
           ld=None, extra_head="", capa=""):
    titulo_aba = MARCA if not titulo else f"{titulo} · {MARCA}"
    itens = [("Início", "/", "inicio"), ("Microtextos", "/microtextos.html", "microtextos"),
             (SECAO_OBRA, "/obra.html", "obra"), ("Sobre", "/sobre.html", "sobre")]
    menu = "".join(
        f'<li><a href="{h}"{" aria-current=" + chr(34) + "page" + chr(34) if k == atual else ""}>{n}</a></li>'
        for n, h, k in itens)
    ld_html = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n' if ld else ""
    c = SOBRE["contato"]
    doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo_aba)}</title>
<meta name="description" content="{e(descricao)}">
<meta name="author" content="{e(AUTOR)}">
<link rel="canonical" href="{url(caminho)}">
<meta property="og:type" content="{tipo}">
<meta property="og:site_name" content="{MARCA}">
<meta property="og:locale" content="pt_BR">
<meta property="og:url" content="{url(caminho)}">
<meta property="og:title" content="{e(titulo or MARCA)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:image" content="{absoluto(imagem)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titulo or MARCA)}">
<meta name="twitter:description" content="{e(descricao)}">
<meta name="twitter:image" content="{absoluto(imagem)}">
<meta name="theme-color" content="#0F1F18">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTES}">
<link rel="stylesheet" href="/assets/site.css">
{ld_html}{extra_head}<script src="/assets/site.js" defer></script>
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo">
<div class="miolo">
<nav class="barra" aria-label="Principal">
<a class="marca" href="/">{MARCA}</a>
<button class="menu-botao" type="button" aria-expanded="false" aria-controls="menu">Menu {IC_MENU}</button>
<ul class="menu" id="menu">{menu}</ul>
</nav>
{capa}</div>
</header>
<main id="conteudo">
{corpo}
</main>
<footer class="rodape">
<div class="miolo">
<div>
<a class="marca" href="/">{MARCA}</a>
<p>{e(AUTOR)} · Diadema, São Paulo</p>
<p><a href="mailto:{e(c['email'])}">{e(c['email'])}</a> · <a href="{e(c['whatsapp_link'])}">{e(c['whatsapp'])}</a></p>
</div>
<ul>
<li><a href="/microtextos.html">Microtextos</a></li>
<li><a href="/obra.html">{SECAO_OBRA}</a></li>
<li><a href="/sobre.html">Sobre</a></li>
</ul>
</div>
</footer>
</body>
</html>
"""
    destino = RAIZ / caminho
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(doc, encoding="utf-8")
    PAGINAS.append(caminho)


def partilha(titulo, resumo, caminho):
    return f"""<div class="partilha">
<p class="rotulo">Compartilhar</p>
<button class="botao vazado" type="button" data-copiar>{IC_LINK} Copiar link</button>
</div>
<p class="aviso partilha-aviso" role="status" aria-live="polite"></p>"""


def comentario(titulo):
    return f"""<form class="comentario" action="{FORMSPREE}" method="POST">
<h2>Envie seu comentário</h2>
<input type="hidden" name="texto" value="{e(titulo)}">
<label for="c-nome">Seu nome (opcional)</label>
<input id="c-nome" type="text" name="nome" autocomplete="name">
<label for="c-msg">Comentário</label>
<textarea id="c-msg" name="mensagem" required></textarea>
<button class="botao escuro" type="submit">Enviar</button>
<p class="aviso" role="status" aria-live="polite"></p>
</form>"""


def vizinhos(antes, depois):
    def um(rot, alvo, classe=""):
        if not alvo:
            return ""
        return (f'<a class="{classe}" href="{alvo[0]}"><span class="rotulo">{rot}</span>'
                f'<span class="nome">{e(alvo[1])}</span><span class="meta">{e(alvo[2])}</span></a>')
    return f'<nav class="vizinhos miolo" aria-label="Outros textos">{um("Texto anterior", antes)}{um("Texto seguinte", depois, "depois")}</nav>'


def ld_artigo(caminho, titulo, descricao, imagem, data=None):
    d = {"@context": "https://schema.org", "@type": "Article", "headline": titulo, "description": descricao,
         "inLanguage": "pt-BR", "image": absoluto(imagem), "mainEntityOfPage": url(caminho),
         "author": {"@type": "Person", "name": AUTOR, "alternateName": MARCA, "url": SITE + "/sobre"},
         "publisher": {"@type": "Person", "name": AUTOR, "alternateName": MARCA}}
    if data:
        d["datePublished"] = data
    return d


# --------------------------------------------------------------- microtextos
def corpo_micro(m):
    blocos = [b.strip() for b in re.split(r"\n\s*\n", m["texto"].strip()) if b.strip()]
    destaque = (m.get("destaque") or "").strip()
    saida = []
    for i, b in enumerate(blocos):
        if i == len(blocos) - 1 and re.fullmatch(r"(★\s*)?tiosantos", b, flags=re.I):
            saida.append(f'<p class="assinatura">{MARCA}</p>')
        elif destaque and b == destaque:
            saida.append(f'<blockquote class="destaque">{e(b)}</blockquote>')
        else:
            saida.append("<p>" + e(b).replace("\n", "<br>") + "</p>")
    return "\n".join(saida)


def midia_micro(m):
    v = m.get("video")
    if not v:
        return ""
    if v.startswith("http"):
        return f'<p><a class="botao vazado" href="{e(v)}" target="_blank" rel="noopener">Assistir no YouTube {SETA}</a></p>'
    v = v if v.startswith("/") else "/" + v
    return f'<video controls preload="metadata"><source src="{e(v)}" type="video/mp4">Seu navegador não reproduz este vídeo.</video>'


def item_lista(m):
    return (f'<li data-tipo="{e(m["tipo"])}"><p class="meta"><span>{data_curta(m["data"])}</span><span>{e(m["tipo"])}</span></p>'
            f'<div><h3><a href="/textos/{m["id"]}.html">{e(m["titulo"])}</a></h3>'
            f'<p class="resumo">{e(m["resumo"])}</p></div></li>')


def paginas_micro(ms):
    for i, m in enumerate(ms):
        caminho = f"textos/{m['id']}.html"
        img = m.get("imagem")
        card = m.get("card") or img or CARD_PADRAO
        figura = (f'<figure class="artigo-imagem"><img src="{e(img)}" alt="" decoding="async"></figure>' if img else "")
        mais_novo = ms[i - 1] if i > 0 else None
        mais_velho = ms[i + 1] if i + 1 < len(ms) else None
        viz = vizinhos(
            (f"/textos/{mais_velho['id']}.html", mais_velho["titulo"], data_curta(mais_velho["data"])) if mais_velho else None,
            (f"/textos/{mais_novo['id']}.html", mais_novo["titulo"], data_curta(mais_novo["data"])) if mais_novo else None)
        corpo = f"""<div class="miolo">
<article class="artigo">
<header class="artigo-cabeca">
<p class="rotulo"><a href="/microtextos.html">Microtextos</a> <span>/ {e(m['tipo'])}</span></p>
<h1>{e(m['titulo'])}</h1>
<p class="linha">{e(m['resumo'])}</p>
<p class="meta">{MARCA} · <time datetime="{m['data']}">{data_longa(m['data'])}</time> · {minutos(m['texto'])} min de leitura</p>
</header>
{figura}
<div class="prosa">
{corpo_micro(m)}
{midia_micro(m)}
</div>
{partilha(m['titulo'], m['resumo'], caminho)}
{comentario(m['titulo'])}
</article>
</div>
{viz}"""
        pagina(caminho, m["titulo"], m["resumo"], corpo, atual="microtextos", imagem=card, tipo="article",
               ld=ld_artigo(caminho, m["titulo"], m["resumo"], card, m["data"]),
               extra_head=f'<meta property="article:published_time" content="{m["data"]}">\n')


def pagina_lista_micro(ms):
    tipos = []
    for m in ms:
        if m["tipo"] not in tipos:
            tipos.append(m["tipo"])
    filtros = '<button class="filtro" type="button" data-tipo="" aria-pressed="true">Todos</button>' + "".join(
        f'<button class="filtro" type="button" data-tipo="{e(t)}" aria-pressed="false">{e(t)}</button>' for t in tipos)
    corpo = f"""<div class="miolo">
<header class="pagina-cabeca">
<h1>Microtextos</h1>
<p>Comentários, crônicas breves e reflexões sobre cultura, arte e cotidiano.</p>
</header>
<div class="filtros" role="group" aria-label="Filtrar por tipo">{filtros}</div>
<ul class="lista">
{chr(10).join(item_lista(m) for m in ms)}
</ul>
<div style="height: 80px"></div>
</div>"""
    pagina("microtextos.html", "Microtextos", "Comentários, crônicas breves e reflexões de tiosantos sobre cultura, arte e cotidiano.",
           corpo, atual="microtextos")


# --------------------------------------------------------------- obra
def link_peca(o):
    return o.get("link") or f"/obra/{o['id']}.html"


def chamada_peca(o):
    tipo = o["tipo"]
    if o.get("audio"):
        acao = "Ler a letra e ouvir"
    elif o.get("video_embed"):
        acao = "Assistir"
    elif tipo.startswith("Poema"):
        acao = "Ler o poema"
    elif tipo == "Ensaio":
        acao = "Ler o ensaio"
    else:
        acao = "Ler"
    return acao


IC_PLAY = ('<svg aria-hidden="true" width="56" height="56" viewBox="0 0 56 56"><circle cx="28" cy="28" r="28" fill="#0F1F18" fill-opacity="0.82"/>'
           '<path d="M23 18l16 10-16 10z" fill="#E3B45C"/></svg>')


def trecho_versos(o, linhas=6):
    """Primeiras linhas da letra ou do poema, para dar vida ao cartão."""
    m = re.search(r'<p class="versos">(.*?)</p>', o.get("corpo", ""), flags=re.S)
    if not m:
        return ""
    ls = [l.strip() for l in m.group(1).strip().split("\n") if l.strip()]
    return "\n".join(ls[:linhas])


def cartao_peca(o):
    alvo = link_peca(o)
    cred = f'<p class="creditos">{e(o["creditos"])}</p>' if o.get("creditos") else ""
    midia = ""
    if o.get("imagem"):
        midia = (f'<a class="peca-midia" href="{alvo}" tabindex="-1" aria-hidden="true">'
                 f'<img src="{e(o["imagem"])}" alt="" loading="lazy" decoding="async"></a>')
    elif o.get("video_embed"):
        vid = o["video_embed"].rstrip("/").split("/")[-1].split("?")[0]
        midia = (f'<a class="peca-midia video" href="{alvo}" tabindex="-1" aria-hidden="true">'
                 f'<img src="https://i.ytimg.com/vi/{e(vid)}/hqdefault.jpg" alt="" loading="lazy" decoding="async">{IC_PLAY}</a>')
    versos = trecho_versos(o) if (o.get("audio") or o["tipo"] == "Poema") else ""
    if versos:
        texto = f'<p class="trecho">{versos}</p>'
    elif o.get("resumo"):
        texto = f'<p>{e(o["resumo"])}</p>'
    else:
        texto = ""
    som = f'<audio controls preload="none" src="{e(o["audio"])}" aria-label="Ouvir {e(o["titulo"])}"></audio>' if o.get("audio") else ""
    acao = "Ler a letra completa" if o.get("audio") else chamada_peca(o)
    return (f'<article class="peca"><p class="rotulo">{e(o["tipo"])}</p>'
            f'<h3><a href="{alvo}">{e(o["titulo"])}</a></h3>{cred}{midia}{texto}{som}'
            f'<a class="link-mono" href="{alvo}" aria-label="{acao}: {e(o["titulo"])}">{acao} {SETA}</a></article>')


def paginas_obra(obra):
    proprias = [o for o in obra if not o.get("link")]
    for i, o in enumerate(proprias):
        caminho = f"obra/{o['id']}.html"
        desc = o.get("resumo") or o.get("creditos") or cortar(o.get("corpo", "")) or o["titulo"]
        img = o.get("imagem")
        partes = []
        if img:
            partes.append(f'<figure class="artigo-imagem"><img src="{e(img)}" alt="{e(o.get("imagem_alt", ""))}" decoding="async">'
                          + (f'<figcaption>{e(o["creditos"])}</figcaption>' if o.get("creditos") else "") + "</figure>")
        if o.get("video_embed"):
            partes.append(f'<div class="video-caixa"><iframe src="{e(o["video_embed"])}" title="{e(o["titulo"])}" loading="lazy" '
                          'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>')
        if o.get("audio"):
            partes.append(f'<div class="tocador"><p class="rotulo">Ouvir</p><audio controls preload="none" src="{e(o["audio"])}"></audio></div>')
        linha = ""
        if o.get("creditos") and not img:
            linha = f'<p class="linha">{e(o["creditos"])}</p>'
        elif o.get("video_embed") and o.get("resumo"):
            linha = f'<p class="linha">{e(o["resumo"])}</p>'
        ant = proprias[i - 1] if i > 0 else None
        prox = proprias[i + 1] if i + 1 < len(proprias) else None
        viz = vizinhos((link_peca(ant), ant["titulo"], ant["tipo"]) if ant else None,
                       (link_peca(prox), prox["titulo"], prox["tipo"]) if prox else None)
        corpo = f"""<div class="miolo">
<article class="artigo">
<header class="artigo-cabeca">
<p class="rotulo"><a href="/obra.html">{SECAO_OBRA}</a> <span>/ {e(o['tipo'])}</span></p>
<h1>{e(o['titulo'])}</h1>
{linha}
</header>
<div class="prosa">
{chr(10).join(partes)}
{o.get('corpo', '')}
</div>
{partilha(o['titulo'], cortar(desc, 120), caminho)}
{comentario(o['titulo'])}
</article>
</div>
{viz}"""
        pagina(caminho, o["titulo"], cortar(desc), corpo, atual="obra", imagem=img or CARD_PADRAO, tipo="article",
               ld=ld_artigo(caminho, o["titulo"], cortar(desc), img or CARD_PADRAO))


def pagina_lista_obra(obra):
    grupos = []
    for nome, tipos in GRUPOS:
        itens = [o for o in obra if o["tipo"] in tipos]
        if itens:
            grupos.append(f'<section class="grupo"><h2>{nome}</h2><div class="grade">{"".join(cartao_peca(o) for o in itens)}</div></section>')
    conhecidos = {t for _, ts in GRUPOS for t in ts}
    resto = [o for o in obra if o["tipo"] not in conhecidos]
    if resto:
        grupos.append(f'<section class="grupo"><h2>Outros</h2><div class="grade">{"".join(cartao_peca(o) for o in resto)}</div></section>')
    corpo = f"""<div class="miolo">
<header class="pagina-cabeca">
<h1>{SECAO_OBRA}</h1>
<p>Escritos, músicas e registros sobre cultura, memória e identidade, em especial sobre Diadema, sua gente e suas histórias.</p>
</header>
{chr(10).join(grupos)}
<div style="height: 88px"></div>
</div>"""
    pagina("obra.html", SECAO_OBRA, "Poemas, crônicas, prosa poética e músicas de tiosantos sobre Diadema, sua gente e suas histórias.",
           corpo, atual="obra")


# --------------------------------------------------------------- sobre
def pagina_sobre():
    d, p, c = SOBRE["depoimento"], SOBRE["perfil"], SOBRE["contato"]
    foto = SOBRE.get("depoimento_imagem")
    figura = (f'<figure class="artigo-imagem"><img src="{e(foto["src"])}" alt="{e(foto.get("alt", ""))}" loading="lazy" decoding="async">'
              f'<figcaption>{e(foto.get("legenda", ""))}</figcaption></figure>') if foto else ""
    blocos = "".join(f'<div><h3>{e(b["titulo"])}</h3><ul>{"".join("<li>" + i + "</li>" for i in b["itens"])}</ul></div>' for b in p["blocos"])
    corpo = f"""<div class="miolo">
<header class="pagina-cabeca">
<h1>Sobre</h1>
<p>{e(AUTOR)}, o {MARCA}. {e(DESCRICAO)}</p>
<p class="atalhos"><a class="link-mono" href="#perfil">Perfil profissional</a><a class="link-mono" href="#depoimento">Depoimento teatral</a><a class="link-mono" href="#contato">Contato</a></p>
</header>
<section class="sobre-bloco" id="perfil" aria-labelledby="perfil-t">
<p class="rotulo">{e(p['rotulo'])}</p>
<h2 id="perfil-t">{e(p['titulo'])}</h2>
<div class="prosa"><p>{p['texto']}</p></div>
<div class="colunas">{blocos}</div>
</section>
<section class="sobre-bloco" id="depoimento" aria-labelledby="depoimento-t">
<p class="rotulo">{e(d['rotulo'])}</p>
<h2 id="depoimento-t">{e(d['titulo'])}</h2>
{figura}
<div class="prosa">
{d['corpo']}
</div>
</section>
<section class="sobre-bloco" id="contato" aria-labelledby="contato-t">
<h2 id="contato-t">Contato</h2>
<p class="contato"><a href="mailto:{e(c['email'])}">{e(c['email'])}</a><a href="{e(c['whatsapp_link'])}">WhatsApp {e(c['whatsapp'])}</a></p>
</section>
</div>"""
    ld = {"@context": "https://schema.org", "@type": "ProfilePage",
          "mainEntity": {"@type": "Person", "name": AUTOR, "alternateName": MARCA, "url": SITE + "/sobre",
                         "homeLocation": {"@type": "Place", "name": "Diadema, São Paulo"}, "description": sem_tags(p["texto"])}}
    pagina("sobre.html", "Sobre", cortar(p["texto"]), corpo, atual="sobre", ld=ld)


# --------------------------------------------------------------- início
def pagina_inicio(ms, obra):
    topo = ms[0]
    img = topo.get("imagem")
    capa_img = (f'<a class="capa-imagem" href="/textos/{topo["id"]}.html" tabindex="-1" aria-hidden="true">'
                f'<img src="{e(img)}" alt="" fetchpriority="high"></a>') if img else ""
    ep = SOBRE["epigrafe"]
    capa = f"""<section class="capa{'' if img else ' sem-imagem'}" aria-label="Texto mais recente">
{capa_img}
<div class="capa-texto">
<p class="rotulo">Mais recente · {data_curta(topo['data'])} · {e(topo['tipo'])}</p>
<h1><a href="/textos/{topo['id']}.html">{e(topo['titulo'])}</a></h1>
<p class="capa-resumo">{e(topo['resumo'])}</p>
<a class="botao ambar cheio-no-celular" href="/textos/{topo['id']}.html">Ler o texto {SETA}</a>
</div>
</section>
<p class="epigrafe-topo">"{e(ep['texto'])}"<cite>{e(ep['autor'])}</cite></p>
"""
    destaques = [o for o in obra if o.get("destaque")] or obra[:3]
    p = SOBRE["perfil"]
    corpo = f"""<section class="secao" aria-labelledby="micro-t">
<div class="miolo">
<div class="cabeca"><h2 id="micro-t">Microtextos</h2><a class="link-mono" href="/microtextos.html">Ver todos os {len(ms)}</a></div>
<ul class="lista">
{chr(10).join(item_lista(m) for m in ms[1:6])}
</ul>
</div>
</section>
<section class="secao faixa-clara" aria-labelledby="obra-t">
<div class="miolo">
<div class="cabeca" style="margin-bottom: 36px"><h2 id="obra-t">{SECAO_OBRA}</h2><a class="link-mono" href="/obra.html">Ver tudo</a></div>
<div class="grade">{"".join(cartao_peca(o) for o in destaques[:3])}</div>
</div>
</section>
<section class="secao" aria-labelledby="sobre-t">
<div class="miolo sobre-chamada">
<h2 id="sobre-t" style="font-size: 40px">Sobre</h2>
<div>
<p class="abre">{e(AUTOR)}, o {MARCA}. Poeta, compositor e cronista de Diadema.</p>
<p class="segue">{p['texto']}</p>
<p class="atalhos"><a class="link-mono" href="/sobre.html#perfil">Perfil profissional</a><a class="link-mono" href="/sobre.html#depoimento">Depoimento teatral</a><a class="link-mono" href="/sobre.html#contato">Contato</a></p>
</div>
</div>
</section>"""
    antigos = {m["id"]: f"/textos/{m['id']}.html" for m in ms}
    antigos.update({"microtextos": "/microtextos.html", "textos": "/obra.html",
                    "depoimento": "/sobre.html#depoimento", "perfil": "/sobre.html#perfil"})
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": MARCA, "url": SITE + "/", "inLanguage": "pt-BR",
          "description": DESCRICAO, "author": {"@type": "Person", "name": AUTOR, "alternateName": MARCA}}
    pagina("index.html", "", f"{AUTOR}, o {MARCA}. {DESCRICAO}", corpo, atual="inicio", ld=ld, capa=capa,
           imagem=topo.get("card") or img or CARD_PADRAO,
           extra_head=f"<script>window.TS_ANTIGOS={json.dumps(antigos, ensure_ascii=False)};</script>\n")


def sitemap(ms):
    from datetime import date
    hoje = date.today().isoformat()
    datas = {f"textos/{m['id']}.html": m["data"] for m in ms}
    extras = ["ensaio-jorge-vargas.html"]
    datas["ensaio-jorge-vargas.html"] = "2026-08-10"
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for c in PAGINAS + extras:
        mod = datas.get(c, max(m["data"] for m in ms) if c in ("index.html", "microtextos.html") else hoje)
        linhas.append(f"  <url><loc>{url(c)}</loc><lastmod>{mod}</lastmod></url>")
    linhas.append("</urlset>")
    (RAIZ / "sitemap.xml").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    PAGINAS = []
    SOBRE = ler("sobre.json")
    MICRO = sorted(ler("textos.json")["microtextos"], key=lambda m: m["data"], reverse=True)
    OBRA = ler("obra.json")["obra"]
    ids = [m["id"] for m in MICRO] + [o["id"] for o in OBRA]
    assert len(ids) == len(set(ids)), "há ids repetidos em textos.json / obra.json"
    pagina_inicio(MICRO, OBRA)
    pagina_lista_micro(MICRO)
    paginas_micro(MICRO)
    pagina_lista_obra(OBRA)
    paginas_obra(OBRA)
    pagina_sobre()
    sitemap(MICRO)
    print(f"{len(PAGINAS)} páginas geradas: {len(MICRO)} microtextos, {len(OBRA)} peças de obra.")
