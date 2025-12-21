RSS_FEEDS = [
    "https://selfh.st/rss/",
    "https://www.eff.org/rss/updates.xml",
    "https://krebsonsecurity.com/feed/",
    "https://www.schneier.com/blog/atom.xml",
    "https://troyhunt.com/rss/",
    "https://www.bleepingcomputer.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://linuxsecurity.com/linuxsecurity_hybrid.xml",
    "https://arstechnica.com/security/feed/",
    "https://www.docker.com/blog/feed/",
    "https://www.aquasec.com/feed/",
    "https://hackaday.com/category/security-hacks/feed/",
    "https://hackaday.com/feed/",
    "https://www.gdprhub.eu/index.php?title=Special:RecentChanges&feed=rss",
    "https://www.404media.co/rss",
]

TELEGRAM_CHAT_ID = {
    574021995: 'https://galdinho.news',
    336581665: 'https://bruzinha.galdinho.news'
}

SCRAPING_MAX_AGE_DAYS_INITIAL = 3

MIN_ARTICLES_FOR_BRIEFING = 10


MIN_INITIAL_FILTER_SCORE = 3

PROMPT_INITIAL_FILTER = """Avalie se este artigo de cibersegurança vale processar para alguém que:
- Mantém servidor próprio com Docker
- Usa Linux Mint
- Valoriza privacidade e soluções descentralizadas
- Quer informações práticas, não só notícias

Título: {title}
Descrição: {description}

CLARAMENTE RELEVANTE (score 4-5):
- Vulnerabilidades em Linux, Docker, containers
- Hardening de servidores, configurações de segurança
- Ferramentas open source de segurança
- Self-hosting seguro, boas práticas
- Privacidade, proteção de dados pessoais
- GDPR, regulamentações europeias de privacidade
- Ataques que afetam infraestrutura self-hosted
- Tutoriais e guias práticos de segurança

CLARAMENTE IRRELEVANTE (score 1-2):
- Segurança corporativa enterprise (SIEM, SOC, compliance corporativo)
- Produtos pagos e soluções proprietárias
- Notícias sobre big techs sem implicação prática
- Criptomoedas e blockchain
- Gaming e entretenimento
- Marketing de produtos de segurança

PODE SER RELEVANTE (score 3):
- Vulnerabilidades em software popular (pode afetar self-hosting)
- Notícias sobre ataques (contexto útil)
- Ferramentas novas que podem ser open source
- Regulamentações que podem ter impacto indireto

ATENÇÃO ESPECIAL - sempre score 4+:
- Palavras-chave: "Docker", "container", "Linux", "self-hosted", "open source", "privacidade", "GDPR", "vulnerabilidade crítica"

Score de 1 a 5. Na dúvida entre 2 e 3, dê 3.

Responda APENAS com o número (1-5)."""


PROMPT_ARTICLE_SUMMARY = """Extraia as informações principais desta notícia de cibersegurança em 2-4 frases diretas.

Priorize informações sobre:
- O QUE aconteceu: vulnerabilidade, ataque, ferramenta, regulamentação
- QUEM é afetado: quais sistemas, softwares, usuários
- O QUE FAZER: se há patch, mitigação, ou ação recomendada
- CONTEXTO TÉCNICO: versões afetadas, CVE se houver, severidade

Para tutoriais e guias:
- Qual problema resolve
- Tecnologias envolvidas
- Nível de complexidade

Ignore ou minimize:
- Declarações vagas de empresas
- Marketing de produtos
- Especulações sobre atribuição de ataques
- Drama corporativo sem impacto técnico

Artigo:
{article_content}

Responda em português brasileiro, de forma direta e técnica."""


PROMPT_IMPACT_RATING = """Avalie o impacto desta notícia de cibersegurança para alguém que:
- Mantém servidor Linux próprio com Docker
- Valoriza privacidade e self-hosting
- Quer saber o que é acionável, não só "interessante"

CRITÉRIOS:

RELEVÂNCIA DIRETA (afeta o setup dela?):
- Vulnerabilidade em Linux, Docker, Nginx, ou software comum de self-hosting?
- Afeta privacidade pessoal ou proteção de dados?
- Envolve ferramentas open source que ela pode usar?
- Regulamentação europeia (GDPR, etc)?

ACIONABILIDADE (dá pra fazer algo?):
- Tem patch ou atualização disponível?
- Oferece configuração ou mitigação prática?
- É um guia ou tutorial que pode ser seguido?
- Ou é só "fique atento" sem ação concreta?

SEVERIDADE TÉCNICA:
- Vulnerabilidade crítica (RCE, escalação de privilégio)?
- Afeta configuração padrão ou precisa de setup específico?
- Exploit já está sendo usado ativamente?

Escala 1-10:
1-2: Irrelevante (corporativo, produto pago, não afeta self-hosting)
3-4: Contexto útil mas sem ação imediata
5-6: Relevante, pode afetar setup comum, vale acompanhar
7-8: Importante, afeta diretamente Linux/Docker/self-hosting, ação recomendada
9-10: Crítico, vulnerabilidade ativa em software comum, atualizar agora

Seja generoso com tutoriais práticos (5-7) mesmo que não sejam "urgentes".
Seja crítico com notícias corporativas sem ação prática (1-3).

Resumo:
"{summary}"

Responda APENAS com o número (1-10)."""


PROMPT_CLUSTER_ANALYSIS = """Você recebeu vários resumos de notícias de cibersegurança relacionadas. Identifique o TEMA CENTRAL.

Resumos:
{cluster_summaries_text}

Responda em 3-5 frases seguindo esta estrutura:

1. Tema central em UMA frase clara
   Exemplos: "Vulnerabilidades críticas em containers Docker"
            "Novas ferramentas open source para hardening de Linux"
            "Atualizações sobre GDPR e proteção de dados na Europa"

2. Tecnologias ou sistemas afetados (seja específica: versões, softwares, configurações)

3. Status atual:
   - Se for vulnerabilidade: há patch? está sendo explorada?
   - Se for ferramenta/guia: qual problema resolve?
   - Se for regulamentação: já está em vigor? afeta quem?

4. O que fazer: ação prática recomendada, se houver

Se os artigos parecerem não relacionados, diga: "Artigos sem tema unificador claro."

Tom: técnico mas acessível. Sem jargão desnecessário, mas sem simplificar demais.

Responda em português brasileiro."""


# ============================================================================
# SÍNTESE DO BRIEFING
# ============================================================================
PROMPT_BRIEF_SYNTHESIS = """Você está escrevendo um resumo de cibersegurança para uma leitora específica.

Perfil da leitora:
- 37 anos, trabalha com QA em Portugal
- Mantém servidor próprio com Linux Mint e Docker
- Gosta de documentação e colocar a mão na massa
- Valoriza soluções descentralizadas e open source
- Não gosta de big techs e soluções proprietárias
- Quer saber: o que aconteceu e o que fazer sobre isso
- Tem senso de humor inteligente, mas leva segurança a sério
- Contato com contexto europeu (GDPR, regulamentações EU)

Você recebeu análises de grupos de notícias relacionadas:

{cluster_analyses_text}

Escreva um resumo em Markdown seguindo esta estrutura:

## Resumo de Segurança

[Parágrafo de abertura: 2-3 frases sobre os temas mais importantes da semana. Priorize: vulnerabilidades acionáveis > ferramentas úteis > contexto regulatório > notícias gerais]

### [Tema 1 - título direto e descritivo]

[2-3 parágrafos. Estrutura sugerida:
- O que aconteceu (fatos, não drama)
- Quem é afetado (seja específica sobre versões e configurações)
- O que fazer (patch, mitigação, configuração)]

### [Tema 2 - título direto e descritivo]

[...]

### [Outros temas se houver]

[...]

TOM:
- Direto e prático, como uma colega técnica explicando
- Técnico quando necessário, mas sempre explicando siglas e conceitos
- Pode ter um toque de humor leve quando apropriado
- "Aqui está o que aconteceu, aqui está o que você pode fazer"

EVITE:
- Alarmismo ("URGENTE!!!", "CRÍTICO!!!")
- Linguagem corporativa ("soluções", "ecossistema", "stakeholders")
- Repetir press releases de empresas
- Assumir que a leitora não entende conceitos técnicos
- Falar de produtos pagos como se fossem a única opção

VALORIZE mencionar:
- Alternativas open source quando existirem
- Links para documentação oficial
- Comandos ou configurações específicas quando relevante
- Contexto europeu (GDPR, regulamentações EU)
- Ferramentas que podem ser self-hosted

Máximo 600 palavras. Responda em português brasileiro."""