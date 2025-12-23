RSS_FEEDS = [
#     "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",  # Folha de S.Paulo
     "https://agenciabrasil.ebc.com.br/rss/politica.xml",  # Agência Brasil
     "https://reporterbrasil.org.br/feed-rss/",  # Repórter Brasil
     "https://www.brasildefato.com.br/rss",  # Brasil de Fato
     "https://www.intercept.com.br/feed/", # The Intercept
     "https://elpais.com/tag/rss/brasil/",  # El País Brasil
     "https://revistaforum.com.br/rss/feed.html", # Revista Fórum
     "https://piaui.folha.uol.com.br/rss/"     
]

DISPLAY_NAME = "Brasil"

TEXT_COLOR = "text-green-800"

TELEGRAM_CHAT_ID = {
   574021995: 'https://galdinho.news',
   336581665: 'https://bruzinha.galdinho.news',
   125774312: 'https://bruzinha.galdinho.news', #Veskinha
   169393478: 'https://bruzinha.galdinho.news' #Juninho
}


# Used in process_articles (operates globally, so uses default)
PROMPT_ARTICLE_SUMMARY ="""Extraia os fatos principais desta notícia em 2-4 frases diretas.

Foque em:
- Quem: pessoas, organizações, instituições envolvidas
- O quê: ações concretas, eventos, anúncios
- Quando: contexto temporal (se relevante)
- Onde: localização geográfica (se relevante)
- Consequências imediatas: o que mudou ou vai mudar

Evite:
- Adjetivos desnecessários
- Opiniões ou análises
- Repetição de informações
- Contextualização histórica (a menos que crucial)

Artigo:
{article_content}

Responda em português brasileiro, de forma direta e factual."""


# Used in rate_articles (operates globally, so uses default)
PROMPT_IMPACT_RATING = """Avalie o impacto desta notícia no contexto brasileiro usando APENAS estes critérios objetivos:

MAGNITUDE (quanto isso afeta?):
- Quantas pessoas são diretamente impactadas?
- É local, estadual, nacional ou internacional?
- Afeta instituições fundamentais (Judiciário, Legislativo, Executivo)?

URGÊNCIA (quão importante é saber disso hoje?):
- É um evento em andamento que pode se desenrolar nas próximas horas/dias?
- Há prazos ou deadlines envolvidos?
- Exige atenção imediata ou é contexto para longo prazo?

RELEVÂNCIA POLÍTICA/SOCIAL (para um leitor de esquerda):
- Trata de direitos fundamentais, desigualdade, justiça social?
- Envolve poder corporativo, concentração de riqueza, exploração?
- Relaciona-se com movimentos sociais, organizações populares?

Escala de 1-10:
1-2: Evento menor, local, sem urgência, impacto limitado
3-4: Relevante regionalmente, alguma urgência, afeta comunidades específicas  
5-6: Nacional, urgência moderada, impacto em milhares/milhões
7-8: Nacional crítico, alta urgência, impacto estrutural ou em instituições
9-10: Histórico, urgência máxima, consequências nacionais profundas

Seja CONSERVADOR: só dê 8+ para eventos realmente extraordinários.

Resumo:
"{summary}"

Responda APENAS com o número (1-10)."""


# Used in generate_brief (can be overridden per profile)
PROMPT_CLUSTER_ANALYSIS = """Você recebeu vários resumos de notícias relacionadas. Identifique o TEMA CENTRAL que conecta estes artigos.

Resumos:
{cluster_summaries_text}

Responda em 3-5 frases seguindo esta estrutura:

1. Tema central em UMA frase (ex: "Disputas sobre demarcação de terras indígenas")
2. Principais atores envolvidos (pessoas, organizações, instituições)
3. Fatos concretos reportados (o que aconteceu, não o que você acha)
4. Status atual (em andamento, resolvido, aguardando desdobramentos)

Se os artigos parecerem não relacionados, diga: "Artigos sem tema unificador claro."

Mantenha tom neutro e descritivo. Sem análise ou opinião.

Responda em português brasileiro."""


# Used in generate_brief (can be overridden per profile)
PROMPT_BRIEF_SYNTHESIS = """Você está escrevendo um resumo de notícias para um leitor brasileiro de esquerda que acompanha política nacional, direitos humanos e questões sociais.

Seu leitor:
- Valoriza jornalismo investigativo (Piauí, Intercept Brasil)
- Interessa-se por movimentos sociais e organizações populares
- Desconfia de poder corporativo e concentração de riqueza
- Quer saber O QUE aconteceu, sem paternalismo ou análise excessiva
- Tem 35 anos, mora em Campinas (estado de São Paulo - Brasil)
- Trabalha com tecnologia (Cientista de Dados)

Você recebeu análises de grupos de notícias relacionadas:

{cluster_analyses_text}

Escreva um resumo em Markdown seguindo esta estrutura:

## Resumo do Dia

[Parágrafo de abertura: 2-3 frases sobre os 3-4 temas mais importantes do dia, em ordem de relevância/urgência]

### [Tema 1 - título direto e descritivo]

[2-4 parágrafos descrevendo os fatos principais deste tema. Use os atores concretos, as ações tomadas, as consequências diretas. Sem adjetivação excessiva.]

### [Tema 2 - título direto e descritivo]

[...]

### [Outros temas]

[...]

TOM: 
- Direto e informativo, como uma boa reportagem
- Sem linguagem corporativa ou "executiva"
- Sem eufemismos quando há injustiça ou exploração
- Prefira voz ativa ("O governo anunciou") a passiva ("Foi anunciado")

EVITE:
- Frases como "é importante notar", "vale destacar", "cabe ressaltar"
- Análises ou previsões ("isso pode indicar", "especialistas acreditam")
- Tom sensacionalista ou alarmista
- Jargão acadêmico ou burocrático

Máximo 600 palavras. Responda em português brasileiro."""


# FILTRO INICIAL PARA DECIDIR QUAL NOTÍCIA IMPORTAR
MIN_INITIAL_FILTER_SCORE = 3

PROMPT_INITIAL_FILTER = """Avalie rapidamente se este artigo brasileiro vale processar.

Título: {title}
Descrição: {description}

CLARAMENTE RELEVANTE (score 4-5):
- Política nacional, estadual ou municipal
- Direitos humanos, desigualdade, justiça social
- Movimentos sociais, greves, manifestações
- Judiciário, legislação, instituições democráticas
- Economia que afeta população (emprego, custo de vida, serviços públicos)
- Questões ambientais e indígenas
- Violência policial, sistema prisional, segurança pública
- Educação e saúde pública

PROVAVELMENTE IRRELEVANTE (score 1-2):
- Esportes, entretenimento, celebridades, fofca
- Horóscopo, astrologia, esoterismo
- Receitas, culinária, lifestyle
- Turismo, viagens, dicas de consumo
- Notícias internacionais sem conexão com Brasil
- Obituários de pessoas não políticas
- Clima/tempo (a menos que seja desastre)

NA DÚVIDA (score 3):
- Pode ter dimensão política mas não está clara no título
- Cultura com possível relevância social
- Economia/negócios que pode afetar trabalhadores

Score de 1 a 5. Seja conservador com 1-2, mas generoso com 3+. É melhor processar alguns artigos médios que perder um importante.

Responda APENAS com o número (1-5)."""