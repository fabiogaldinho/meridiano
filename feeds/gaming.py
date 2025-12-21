RSS_FEEDS = [
     "https://www.eurogamer.net/feed",
     "https://www.vg247.com/feed/articles",
     "https://www.vg247.com/feed/news",
     "https://www.gamedeveloper.com/rss.xml",
     "https://www.polygon.com/feed/",
     "https://aftermath.site/rss/",
     "https://gameinformer.com/news.xml?_gl=1*1ocx7ox*_up*MQ..*_ga*NTgwNjg5MTI4LjE3NjM4MDUwODg.*_ga_PX9YKWLVPB*czE3NjM4MDUwODckbzEkZzEkdDE3NjM4MDUwODckajYwJGwwJGgw",
     "https://gameinformer.com/features.xml?_gl=1*1ocx7ox*_up*MQ..*_ga*NTgwNjg5MTI4LjE3NjM4MDUwODg.*_ga_PX9YKWLVPB*czE3NjM4MDUwODckbzEkZzEkdDE3NjM4MDUwODckajYwJGwwJGgw",
     "https://thisweekinvideogames.com/feed/",
     "https://remapradio.com/rss/",
     "https://www.rockpapershotgun.com/feed",
     "https://kotaku.com/feed",
     "https://www.pastemagazine.com/games/rss",
     "https://www.destructoid.com/feed/",
     "https://www.videogameschronicle.com/feed/"
]

TELEGRAM_CHAT_ID = {
   574021995: 'https://galdinho.news',
   336581665: 'https://bruzinha.galdinho.news'
}

# Used in process_articles (operates globally, so uses default)
PROMPT_ARTICLE_SUMMARY = """Extraia as informações principais deste artigo sobre jogos em 2-4 frases diretas.

TIPO DE CONTEÚDO
Identifique primeiro (não precisa apresentar isto no resumo):
- Review/crítica de jogo específico
- Notícia sobre lançamento/anúncio
- Análise da indústria (condições de trabalho, tendências, negócios)
- Ensaio/análise cultural sobre jogos ou temas em jogos
- Notícia sobre desenvolvimento (cancelamento, mudança de estúdio, etc)

INFORMAÇÕES ESSENCIAIS:
Para reviews/análises de jogos:
- Nome do jogo, plataformas, desenvolvedor/publisher
- Gênero e principais mecânicas
- Temas narrativos ou culturais (se relevante)
- Avaliação geral (se for review)

Para notícias de indústria:
- Empresa/estúdio envolvido
- Fato concreto (demissão, aquisição, sindicalização, crunch)
- Número de pessoas afetadas (se aplicável)
- Contexto político/trabalhista

Para análises culturais/ensaios:
- Tema central da análise
- Jogos ou conceitos discutidos
- Argumento ou perspectiva principal

EVITE:
- Spoilers não marcados
- Hype marketing sem substância
- Repetir press releases sem análise

Artigo:
{article_content}

Responda em português brasileiro, mantendo nomes de jogos em inglês quando apropriado."""


# Used in rate_articles (operates globally, so uses default)
PROMPT_IMPACT_RATING = """Avalie a relevância deste artigo de jogos usando estes critérios:

PROFUNDIDADE E QUALIDADE:
- É análise profunda (ensaio, crítica cultural) ou notícia rasa (trailer, screenshot)?
- Vai além da superfície em temas, narrativa, ou questões?
- Traz perspectiva original ou apenas repete informação básica?

RELEVÂNCIA TEMÁTICA:
Pontos altos para conteúdo sobre:
- Condições de trabalho, crunch, sindicalização na indústria
- Representação LGBTQ+, racial, de gênero em jogos
- Narrativas complexas, temas maduros, design de jogos inovador
- Crítica à indústria AAA, monetização predatória, crunch
- Jogos narrativos (aventura, puzzle, horror psicológico)
- Exclusivos ou jogos notáveis para PS5/Switch

Pontos baixos para:
- Apenas gráficos ou performance técnica sem contexto
- Lançamentos de jogos mobile ou gacha sem análise crítica
- Trailers/anúncios sem informação substantiva
- Competitivo/esports sem conexão com questões maiores

ESCOPO E IMPORTÂNCIA:
- Afeta a indústria inteira ou apenas um jogo/empresa?
- É sobre jogo AAA importante, indie relevante, ou nicho?
- Estabelece precedente (legal, cultural, de design)?

TIPO DE CONTEÚDO:
- Ensaio/análise profunda: +2 pontos base
- Review completa: score normal
- Notícia de indústria: avaliar por impacto trabalhista
- Anúncio/trailer sozinho: geralmente 1-3

Escala 1-10:
1-2: Trailer vazio, screenshot, notícia menor sem análise
3-4: Lançamento menor, review rasa, notícia interessante mas limitada
5-6: Review sólida OU notícia importante de indústria OU jogo indie relevante
7-8: Análise profunda excepcional OU questão trabalhista séria OU jogo AAA importante
9-10: Ensaio cultural definitivo OU mudança estrutural na indústria OU jogo histórico

ATENÇÃO:
- Profundidade pode compensar falta de urgência (ensaio sobre jogo antigo pode ser 7+)
- Questões trabalhistas sempre merecem score alto
- Review de jogo narrativo importante vale mais que anúncio de jogo qualquer

Resumo:
"{summary}"

Responda APENAS com o número (1-10)."""


# Used in generate_brief (can be overridden per profile)
PROMPT_CLUSTER_ANALYSIS = """Você recebeu vários resumos de artigos sobre jogos. Identifique o TEMA CENTRAL que conecta estes artigos.

Resumos:
{cluster_summaries_text}

Responda em 3-5 frases seguindo esta estrutura:

1. Tema central em UMA frase clara
   Exemplos: "Condições de trabalho em estúdios AAA"
            "Representação LGBTQ+ em jogos indie de 2025"
            "Reviews de jogos narrativos para console"
            "Monetização e práticas predatórias em live service"

2. Jogos, estúdios, ou desenvolvedores específicos mencionados

3. Se for análise crítica: temas/argumentos principais
   Se for notícia de indústria: fatos concretos e impactos
   Se forem reviews: consenso geral ou divergências

4. Conexão entre os artigos (o que os une além do tema óbvio?)

Se os artigos parecerem não relacionados, diga: "Artigos sem tema unificador claro."

Atenção especial para:
- Padrões de abuso ou exploração na indústria
- Discussões sobre narrativa, representação, ou design
- Múltiplas perspectivas sobre o mesmo jogo ou questão
- Conexões entre jogos aparentemente diferentes

Mantenha nomes de jogos em inglês. Resto em português brasileiro."""


# Used in generate_brief (can be overridden per profile)
PROMPT_BRIEF_SYNTHESIS = """Você está escrevendo um resumo de notícias de jogos para um leitor brasileiro que ama jogos narrativos, análise cultural de games, e se preocupa com a indústria de jogos como espaço de trabalho criativo e expressão política.

Seu leitor:
- Joga em PS5 e Switch, valoriza tanto AAA narrativos quanto indies experimentais
- Favorece jogos como The Last of Us, Inside, 1000xResist, Overwatch 2
- Se alinha politicamente com Remap, Aftermath, Tecnologia e Classe
- Quer saber sobre condições de trabalho, representação, narrativas complexas
- Lê reviews mas valoriza ainda mais análises culturais profundas
- É crítico de monetização predatória e práticas corporativas abusivas
- Celebra bons jogos mas não é acrítico da indústria

Você recebeu análises de grupos de notícias relacionadas:

{cluster_analyses_text}

Escreva um resumo em Markdown seguindo esta estrutura:

## Resumo de Jogos

[Parágrafo de abertura: 2-3 frases sobre os temas mais interessantes - priorize análises profundas, questões de indústria, e jogos narrativamente relevantes sobre simples anúncios]

### [Tema 1 - título descritivo e específico]

[2-4 parágrafos. Para reviews: contextualize o jogo e mencione consenso crítico. Para análises culturais: explore o argumento. Para notícias de indústria: seja claro sobre impacto em trabalhadores.]

### [Tema 2]

[...]

### [Outros temas]

[...]

TOM:
- Entusiasmado com jogos bons, crítico de práticas ruins
- Sério com análise mas não pretensioso ou acadêmico demais
- Político quando relevante, sem forçar política onde não cabe
- Celebra criatividade e arte em jogos
- Chame crunch de crunch, exploração de exploração

VALORIZE mencionar:
- Desenvolvedores (não só publishers) - credite o trabalho criativo
- Aspectos narrativos e temáticos dos jogos
- Questões de representação quando presentes
- Plataformas (especialmente PS5/Switch quando exclusivos)
- Estúdios indie e AA que fazem trabalho interessante
- Análises que vão além do superficial

EVITE:
- Linguagem de marketing ("experiência épica", "jornada emocionante")
- Focar só em gráficos ou performance sem contexto
- Tratar publishers como se fossem os criadores dos jogos
- Hype acrítico de AAA sem mencionar contexto (crunch, monetização)
- Assumir que "diversão" é única métrica de qualidade
- Spoilers não sinalizados

SOBRE REVIEWS:
- Mencione se há consenso crítico ou divergência
- Destaque perspectivas únicas ou análises profundas
- Contextualize gênero e expectativas
- Se for jogo narrativo, sinalize isso

SOBRE INDÚSTRIA:
- Sempre centralize impacto em trabalhadores, não em empresas
- Demissões em massa não são "reestruturação", são demissões em massa
- Crunch não é "dedicação", é exploração

Máximo 700 palavras. Mantenha nomes de jogos em inglês. Resto em português brasileiro."""


# FILTRO INICIAL PARA DECIDIR QUAL NOTÍCIA IMPORTAR
MIN_INITIAL_FILTER_SCORE = 3

PROMPT_INITIAL_FILTER = """Avalie rapidamente se este artigo sobre jogos vale processar.

Título: {title}
Descrição: {description}

CLARAMENTE RELEVANTE (score 4-5):
- Condições de trabalho: crunch, demissões, sindicalização em estúdios
- Análises culturais, ensaios sobre narrativa, design, representação
- Reviews de jogos (qualquer jogo, indie ou AAA)
- Questões de representação LGBTQ+, racial, de gênero
- Cancelamentos de jogos, mudanças em estúdios, falências
- Monetização predatória, loot boxes, práticas antiéticas
- Jogos narrativos, horror, puzzle, aventura
- Exclusivos importantes de console

CLARAMENTE IRRELEVANTE (score 1-2):
- Patch notes, updates técnicos menores
- Skins, cosméticos, itens de loja
- Rankings de jogadores, resultados de torneio (sem análise)
- Jogos mobile gacha sem análise crítica
- Códigos promocionais, ofertas, descontos
- Hardware puro (PC, periféricos) sem conexão com jogos
- Esport, time de esport

PODE SER RELEVANTE (score 3):
- Anúncios de jogos que parecem interessantes mas sem detalhes
- Trailers que podem revelar direção narrativa
- Notícias sobre empresas de jogos sem ângulo trabalhista claro
- DLCs ou expansões de jogos conhecidos
- Eventos de jogos (conferências, showcases)

ATENÇÃO: Análises profundas e ensaios sempre merecem score alto, mesmo sobre jogos antigos. Profundidade compensa falta de urgência.

Score de 1 a 5. Seja generoso com reviews e análises (score 4-5), crítico com marketing vazio (score 1-2).

Responda APENAS com o número (1-5)."""