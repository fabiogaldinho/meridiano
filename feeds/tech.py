RSS_FEEDS = [
  "https://techcrunch.com/feed/",
  "https://www.theverge.com/rss/index.xml",
  "https://arstechnica.com/feed/",
  "https://krebsonsecurity.com/feed/",
  "https://feeds.feedburner.com/TheHackersNews",
  "https://www.bleepingcomputer.com/feed/",
  "https://www.tomshardware.com/feeds/all",
  "https://www.wired.com/feed/category/backchannel/latest/rss",
  "https://www.wired.com/feed/rss",
  "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
  "https://www.404media.co/rss",
  "https://theintercept.com/feed/",
  "https://wccftech.com/feed/",
  "https://www.engadget.com/rss.xml",
  "https://techcrunch.com/feed/",
  "https://www.wired.com/rss/",
  "https://gizmodo.com/feed"
]

pt_br = "Responda em português brasileiro."

# Used in process_articles (operates globally, so uses default)
PROMPT_ARTICLE_SUMMARY = """Extraia os fatos principais desta notícia de tecnologia em 2-4 frases diretas.

Priorize informações sobre:
- Regulações, leis, políticas governamentais sobre tech
- Condições de trabalho em empresas de tecnologia
- Movimentos de trabalhadores, sindicatos, organizações
- Pesquisas científicas e avanços técnicos concretos
- Vulnerabilidades de segurança e suas implicações
- Concentração de poder corporativo e antitruste
- Uso político ou social de tecnologia

Ignore ou minimize:
- Lançamentos de produtos comerciais
- Valorações de mercado e movimento de ações
- Opinões de CEOs e executivos (a menos que politicamente relevantes)
- Marketing corporativo disfarçado de notícia

Formato:
- Quem: empresas, governos, trabalhadores, pesquisadores envolvidos
- O quê: ações concretas, mudanças, descobertas
- Impacto material: quem ganha, quem perde, o que muda no mundo real

Artigo:
{article_content}

Responda em português brasileiro."""


# Used in rate_articles (operates globally, so uses default)
PROMPT_IMPACT_RATING = """Avalie o impacto desta notícia de tecnologia usando estes critérios:

RELEVÂNCIA TEMÁTICA (alinha com interesses específicos?):
- Regulação de big techs, antitruste, quebra de monopólios?
- Trabalho precário em tech, condições de desenvolvedores, sindicatos?
- Vigilância, privacidade, uso político de plataformas?
- Pesquisa científica de base (IA, computação, etc) com implicações sociais?
- Segurança crítica que afeta infraestrutura ou pessoas?
- Crítica ao capitalismo tech, economia de atenção, plataformização?

MAGNITUDE E ALCANCE:
- Afeta apenas uma empresa/produto ou toda uma indústria?
- É local, nacional, global?
- Muda estruturalmente como tecnologia funciona na sociedade?
- Estabelece precedente legal ou técnico importante?

URGÊNCIA E ATUALIDADE:
- É um desenvolvimento novo ou discussão antiga reciclada?
- Tem implicações imediatas ou é contexto de longo prazo?
- Requer atenção agora ou é "interessante de saber"?

Escala 1-10:
1-2: Lançamento de produto, notícia corporativa menor, irrelevante politicamente
3-4: Relevante para um nicho, sem impacto estrutural
5-6: Afeta indústria inteira OU muito relevante politicamente
7-8: Mudança estrutural importante E relevante politicamente
9-10: Histórico, muda fundamentalmente relação sociedade-tecnologia

Seja ESPECIALMENTE crítico com:
- Notícias sobre valoração de empresas (geralmente 1-2)
- Lançamentos de produtos sem implicação política (1-3)
- Declarações de CEOs sem ação concreta (1-3)

Resumo:
"{summary}"

Responda APENAS com o número (1-10)."""


# Used in generate_brief (can be overridden per profile)
PROMPT_CLUSTER_ANALYSIS = """Você recebeu vários resumos de notícias de tecnologia relacionadas. Identifique o TEMA CENTRAL que conecta estes artigos.

Resumos:
{cluster_summaries_text}

Responda em 3-5 frases seguindo esta estrutura:

1. Tema central em UMA frase (ex: "Regulação europeia de IA e resistência das big techs")
2. Atores principais (empresas, governos, trabalhadores, pesquisadores, organizações)
3. Fatos técnicos ou políticos concretos (novas leis, descobertas, vulnerabilidades, ações)
4. Estado atual e possíveis desdobramentos próximos

Se os artigos parecerem não relacionados, diga: "Artigos sem tema unificador claro."

Atenção especial para:
- Conflitos entre interesse corporativo e interesse público
- Movimentos de trabalhadores ou usuários contra empresas
- Mudanças regulatórias significativas
- Avanços científicos com implicações sociais

Mantenha tom técnico mas acessível. Sem jargão desnecessário.

Responda em português brasileiro."""


# Used in generate_brief (can be overridden per profile)
PROMPT_BRIEF_SYNTHESIS = """Você está escrevendo um resumo de notícias de tecnologia para um leitor brasileiro de esquerda, crítico de big techs e do capitalismo de plataforma.

Seu leitor:
- Valoriza análise materialista de tecnologia (Tecnologia e Classe)
- Interessa-se por regulação, trabalho em tech, uso político de plataformas
- É crítico de concentração corporativa e economia acionária
- Valoriza pesquisa científica real, não marketing de produto
- Quer entender implicações sociais e políticas da tecnologia
- Tem 35 anos, mora em Campinas (estado de São Paulo - Brasil)
- Trabalha com tecnologia (Cientista de Dados)

Você recebeu análises de grupos de notícias relacionadas:

{cluster_analyses_text}

Escreva um resumo em Markdown seguindo esta estrutura:

## Resumo de Tecnologia

[Parágrafo de abertura: 2-3 frases sobre os 3-4 temas mais importantes, priorizando regulação, trabalho, e mudanças estruturais]

### [Tema 1 - título direto e descritivo]

[2-4 parágrafos descrevendo os fatos principais. Seja específico sobre tecnologias, empresas, regulações. Use termos técnicos quando necessário mas explique-os.]

### [Tema 2 - título direto e descritivo]

[...]

### [Outros temas]

[...]

TOM:
- Técnico mas acessível - explique conceitos quando necessário
- Crítico de poder corporativo sem ser panfletário
- Valorize trabalho e pesquisa sobre produto e mercado
- Chame as coisas pelos nomes reais (demissão, não "reestruturação")

EVITE:
- Linguagem corporativa ("ecossistema", "disrupção", "inovação" sem contexto)
- Tratamento acrítico de empresas ou executivos
- Repetir press releases como se fossem notícias
- Assumir que tecnologia = progresso automático
- Jargão técnico sem explicação (mas use termos técnicos quando adequado)

VALORIZE mencionar:
- Aspectos regulatórios e legais concretos
- Implicações para trabalhadores e usuários
- Concentração de poder e dados
- Alternativas abertas, cooperativas, públicas

Máximo 600 palavras. Responda em português brasileiro."""


# FILTRO INICIAL PARA DECIDIR QUAL NOTÍCIA IMPORTAR
MIN_INITIAL_FILTER_SCORE = 4

PROMPT_INITIAL_FILTER = """Avalie rapidamente se este artigo de tecnologia vale processar.

Título: {title}
Descrição: {description}

CLARAMENTE RELEVANTE (score 4-5):
- Regulação governamental de tech, antitruste, leis de privacidade
- Condições de trabalho: demissões em massa, crunch, sindicalização
- Vigilância, privacidade, uso político de plataformas
- Segurança: vulnerabilidades críticas, ataques, vazamentos de dados
- Pesquisa científica em IA, computação, criptografia
- Aquisições que concentram poder, mudanças estruturais na indústria
- Conteúdo de mídia sobre práticas corporativas

CLARAMENTE IRRELEVANTE (score 1-2):
- Lançamentos de produtos de consumo (novo iPhone, atualização de app)
- Valoração de startups, rodadas de investimento, IPOs
- Reviews de gadgets e dispositivos
- Tutoriais, dicas de uso, guias de compra
- Rumores sobre produtos futuros
- Marketing disfarçado de notícia
- Movimentação de executivos sem contexto político

PODE SER RELEVANTE (score 3):
- Produto novo mas com implicações de privacidade/segurança
- Mudanças em plataformas grandes que afetam usuários
- Pesquisa científica em áreas menos críticas
- Negócios tech com ângulo trabalhista não claro no título

ATENÇÃO ESPECIAL - sempre score 4+:
- Palavras-chave: "regulação", "antitruste", "demissão", "sindicato", "vazamento", "vulnerabilidade", "privacidade", "vigilância"

Score de 1 a 5. Seja MUITO crítico com score 1-2 para lançamentos de produto e valorações. Na dúvida entre 2 e 3, dê 3.

Responda APENAS com o número (1-5)."""