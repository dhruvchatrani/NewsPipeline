# Autonomous News Agent 

An autonomous system designed to identify trending global events, filter them for impact, and generate high-quality, fact-grounded articles without human intervention.

##  Objective
This project implements a complete news pipeline capable of:
1.  **Ingestion**: Fetching trending data via APIs, RSS, and scrapers.
2.  **Selection**: Filtering noise to identify the top **3-5** significant global trends (configured in `config.yaml`).
3.  **Research**: Gathering factual context from real-time sources using recursive gap-filling.
4.  **Generation**: Writing publication-ready articles (600-800 words) grounded in research.
5.  **Output**: Delivering a structured JSON payload for external consumption.

##  Quick Start

### Prerequisites
*   Python 3.10+
*   API Keys: **Google Gemini API**, **Tavily API**, **NewsAPI API**

### Installation
```bash
git clone <repository-url>
cd NewsPipeline
pip install -r requirements.txt
```

### Configuration
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=
TAVILY_API_KEY=
NEWS_API_KEY=
```
>Contact [Dhruv Chatrani](mailto:dhruv.chatrani@gmail.com) for API keys.

##  Usage Guide

### 1. Traditional CLI 
```bash
python3 main.py [Region]
# Regions: Global, US, India
```

### 2. Streamlit Dashboard (Recommended)
```bash
streamlit run src/ui/dashboard.py
```

### 3. REST API 
Start the server:
```bash
uvicorn src.api.main:app --reload
```
Trigger a run:
```bash
curl -X POST "http://localhost:8000/run?region=US"
```
##  Brief Documentation

### 1. Approach: Architecture & Stack
The NewsPipeline is built using **LangGraph** to model the news lifecycle as a robust state machine. We chose a **Multi-Agent Orchestration** approach over simple sequential chains to enable **self-correction loops** (e.g., verifying an article against its research and re-writing if factual gaps are found). 
- **LLM**: Google Gemini 2.5 Flash for its high context window and reasoning speed.
- **Search**: Tavily for specialized AI-native research that supports "Recursive Gap Filling".
- **Interface**: Streamlit for a premium, real-time dashboard experience.

### 2. Trade-offs: Speed, Cost, & Factuality
- **Factuality over Speed**: We implemented a recursive research step that performs follow-up searches for "gaps" in initial data. While this increases execution time by ~15-20 seconds per article, it significantly reduces hallucinations.
- **Cost-Efficiency**: We utilize Gemini 2.5 Flash, which provides near-Pro performance for specific reasoning tasks at a fraction of the cost, ensuring daily runs are sustainable.
- **Modular vs Monolithic**: The system is split into distinct nodes (Ingest, Select, Research, Generate, Verify). This makes debugging easier but requires more rigorous state management via LangGraph.

### 3. Trend Logic: How `trend_score` is Calculated
The `trend_score` (0-10) is a weighted calculation performed by the `SelectionAgent` (Gemini) based on a configured **Scoring Matrix**:
- **Geopolitical Impact (40%)**: Does this event affect international relations or regional stability?
- **Economic Consequences (30%)**: Does it impact markets, supply chains, or global finance?
- **Human Interest (30%)**: Is the story compelling at a social or personal level?

Before scoring, the system executes a **Deduplication** step using TF-IDF and Cosine Similarity to merge overlapping headlines (e.g., "BTC Price Surge" and "Bitcoin hits record high") into a single trend, ensuring only unique, high-impact stories move to the research phase.

##  Full Instructions
For a detailed guide on environment setup and execution, please see [RUN_INSTRUCTIONS.md](docs/RUN_INSTRUCTIONS.md).

##  Architecture Overview
For detailed information on the RAG implementation and state transitions, please refer to [TECHNICAL_DETAILS.md](docs/TECHNICAL_DETAILS.md)

<details>
  <summary>Click to view Sample Output</summary>

```json
{
  "date": "2026-02-18",
  "execution_time_seconds": 262.09,
  "articles": [
    {
      "title": "’Death is Not Speculative’: Lawyers Warn of Lethal Risks for Haitian TPS Holders Facing Deportation",
      "category": "Politics",
      "trend_score": 7,
      "summary": "Lawyers representing Haitian TPS holders have filed new documents, presenting harrowing evidence of intensified violence and murder in Haiti to support a stay against deportation. They argue that the risk of death for returning immigrants is \"not speculative,\" citing recent decapitation deaths of four deported women and widespread kidnappings by ruthless criminal groups.",
      "article_body": "# ’Death is Not Speculative’: Lawyers Warn of Lethal Risks for Haitian TPS Holders Facing Deportation\n\nSPRINGFIELD – A fierce legal battle over the fate of thousands of Haitian immigrants holding Temporary Protected Status (TPS) intensified this week as their legal representatives filed compelling new documents in federal court. On Monday, February 16, 2026, these attorneys presented a robust memorandum emphatically supporting a stay against the termination of Haitian TPS, a critical measure designed to protect individuals from returning to a country in crisis. This move comes in the wake of a federal judge's previous denial of the Trump administration's appeals to end the special status, underscoring the ongoing judicial scrutiny of the issue. The new filing delivers a stark and unvarnished account of the extreme and life-threatening dangers that await their clients if they are compelled to return to Haiti, a nation currently grappling with a severe humanitarian emergency. With the U.S. government slated to submit its counter-reply by Thursday, the coming days are pivotal in determining the security and future of these vulnerable individuals who have sought refuge in the United States.\n\nThe newly filed court documents paint a grim picture of Haiti, describing a nation where \"criminal groups... have intensified attacks on the population and infrastructure, paralyzing much of the nation and creating one of the most dire humanitarian situations in the world.\" This stark assessment is underscored by recent, harrowing reports. As news outlets detailed on February 4, just two weeks prior to the legal filing, the bodies of four Haitian women, who had been deported from the United States several months earlier, were discovered decapitated and dumped in a river.\n\nThis brutal incident serves as a chilling testament to the dangers at hand, directly referenced by the lawyers in their filing. They asserted, unequivocally, that \"The risk of death is not speculative. Just two weeks ago, the bodies of four Haitian women deported from the U.S. several months earlier were found decapitated and dumped in a river.\" This statement powerfully refutes any suggestion that the threats faced by returning Haitians are theoretical or exaggerated.\n\nNews Center 7's Malik Patterson spoke with Viles Dorsainvil, President of the Haitian Community Help & Support Center, who echoed the lawyers' grave concerns. Dorsainvil did not mince words, stating, \"The hoodlums in Haiti are merciless.\" He conveyed the profound fear gripping Haitian immigrants at the prospect of being sent back, explaining, \"When they kidnap a person, you are exposed to torture, and you can even be killed. So that’s the reality in Haiti.\"\n\nDespite the pervasive fear, Dorsainvil clarified that the desire to return to their roots remains strong among the community. \"It’s not a question that we don’t want to go back to Haiti. Haiti is our country,\" he affirmed. However, this innate longing is tempered by a crucial condition: \"We don’t have any problem going back there, but at least there should be a level of peace and security that would allow us to go back to our country.\" His words highlight the deep emotional ties to their homeland, juxtaposed against the impossible reality of the current security vacuum.\n\nThis critical legal filing and the horrific, irrefutable evidence it presents cast a stark light on the profound challenges confronting federal courts tasked with balancing immigration policy objectives against paramount humanitarian concerns. The very essence of Temporary Protected Status, conceived to safeguard individuals from returning to countries ravaged by conflict, natural disasters, or other extraordinary and impermanent circumstances, is now at the forefront of this debate. In Haiti’s context, the \"temporary\" designation has stretched over years, mirroring an entrenched state of instability that, far from improving, has precipitously worsened. The lawyers' assertion that \"the risk of death is not speculative\" elevates the discussion from abstract policy to a tangible threat to human life.\n\nThe current situation in Haiti, where criminal syndicates wield paralyzing power and ignite a widespread humanitarian catastrophe, poses a formidable challenge to international principles governing the safe and voluntary repatriation of individuals. For the thousands of Haitian TPS holders in the United States, the legal fight for their protected status transcends mere administrative procedure; it is, quite literally, a struggle for survival. The imminent outcome of this motion, contingent on the government’s forthcoming reply, will not only dictate the immediate destinies of these individuals but could also establish a significant precedent. It will define how the U.S. judiciary and government respond to demonstrably deteriorating conditions in nations whose citizens have been granted TPS, forcing a direct confrontation with the stark choice between adherence to policy and the imperative to protect human life in the face of extreme, verified danger. The message from their legal advocates is unambiguous: the threat is not imagined, it is immediate, pervasive, and potentially fatal.",
      "sources": [
        "https://www.whio.com/news/local/death-is-not-speculative-lawyers-representing-tps-holders-say-returning-haiti-risks/SJNEOKUON5FL7OFW35M5YBFROY/",
        "https://www.yahoo.com/news/articles/death-not-speculative-lawyers-representing-182251874.html",
        "https://www.youtube.com/watch?v=M0Jr5d-xcNI"
      ],
      "hallucination_check": "Pass"
    },
    {
      "title": "Trump Bets on Diplomacy Without Diplomats - The New York Times",
      "category": "Politics",
      "trend_score": 6.5,
      "summary": "President Trump is recalibrating American foreign policy by entrusting high-stakes negotiations to personal envoys Steve Witkoff and Jared Kushner, eschewing traditional diplomatic channels for urgent talks on Iran and Ukraine. This unconventional approach marks a significant departure, shaping global relations amidst rising geopolitical tensions and concerns among U.S. allies.",
      "article_body": "# Trump Bets on Diplomacy Without Diplomats\n\n**Washington D.C.** — In a dramatic shift for American foreign policy, President Trump is increasingly relying on a tight circle of trusted, non-traditional envoys to navigate some of the world's most perilous geopolitical challenges. At the forefront of these efforts are real estate developer Steve Witkoff and the President's son-in-law, Jared Kushner, who have been tasked with leading sensitive negotiations concerning Iran and the ongoing conflict in Ukraine.\n\nThis unconventional strategy, as detailed by David E. Sanger and Anton Troianovski, signals a clear departure from established diplomatic norms, prompting both intrigue and concern across international capitals. Their involvement comes at a critical juncture, with indirect talks between American and Iranian officials recently concluding in Geneva, yielding what an Iranian official described as \"good progress\" and an agreement on \"a set of guiding principles.\"\n\nThe urgency surrounding these discussions is palpable. President Trump himself indicated he would be involved in the talks \"indirectly,\" emphasizing their \"very important\" nature and expressing a belief that Iran desired a deal. This diplomatic push follows a period of heightened tensions, marked by a significant U.S. military buildup in the region, including the deployment of two aircraft carriers, after President Trump vowed support for anti-government demonstrators in Iran. Those protests, however, were met with a bloody crackdown, resulting in thousands of deaths according to human rights groups.\n\nParallel to the Iran discussions, Witkoff, the Middle East envoy, and Kushner have been positioned at the center of the Russia-Ukraine war negotiations. Trilateral talks in Geneva have reportedly focused on the contentious issue of Ukrainian-held territory in the east, which Russia seeks to control as a condition for peace – a demand Kyiv has firmly stated is a \"nonstarter.\"\n\nThis reliance on dealmakers rather than career diplomats extends beyond these immediate crises. The President's approach has been characterized by a willingness to engage directly and often unpredictably. For instance, facing an immigration backlash, President Trump recently called Senate Democrat Chuck Schumer to cut a deal, agreeing to work on new limits for federal immigration agents and keep the government open. Such instances highlight a transactional, direct-negotiation style that permeates his foreign and domestic policy.\n\nThe broader implications of this diplomatic paradigm are far-reaching. Internationally, President Trump's unpredictability has prompted European leaders to openly discuss \"de-risking\" from the United States, raising questions about the future of transatlantic alliances. As Steven Erlanger and David E. Sanger reported from Munich, European allies were left wondering \"what kind of alliance they were left with\" after a series of confusing messages from the U.S. delegation.\n\nFurther complicating the global security landscape, President Trump has weighed the prospect of increasing nuclear arms and resuming underground tests. This development comes as the U.S. and Russia find themselves without a nuclear arms control agreement for the first time in decades, sparking fears of a new arms race. David E. Sanger and William J. Broad have explored whether this is an attempt to spur new negotiations or an embrace of unchecked nuclear expansion.\n\nEconomically, the administration's tariff policies continue to reshape global trade. While President Trump credits \"Mister Tariff\" for the country's strength, economists often disagree, suggesting that U.S. economic growth appears to be despite tariffs, not because of them. Japan, in a strategic move to avoid Mr. Trump’s tariffs, recently announced $36 billion in U.S. investments, a first step in a larger $550 billion pledge aimed at securing tariff relief and sustaining U.S. relations. Meanwhile, the President rolled out a $12 billion bailout for farmers, an acknowledgment of the domestic impact of his trade policies.\n\nThe President's focus on Iran has also drawn scrutiny, with analyst Thomas L. Friedman observing that Prime Minister Netanyahu has \"gotten Trump to focus on Iran and ignore the destructive things Bibi is doing in Gaza, in the West Bank and inside Israel.\" This suggests a transactional foreign policy where certain regional interests may be prioritized or overlooked in the pursuit of larger, more visible deals.\n\nAs Massimo Calabresi noted, if alliances continue to erode and instability spreads, America may be headed for \"more, not fewer, international entanglements.\" The Trump administration’s bet on diplomacy without career diplomats is undeniably reshaping the global order, pushing the boundaries of traditional statecraft in an increasingly volatile world. The success or failure of Witkoff and Kushner's high-stakes assignments may ultimately define this audacious approach to international relations.\n",
      "sources": [
        "https://www.nytimes.com/2026/02/17/us/politics/trump-witkoff-kushner-diplomacy.html",
        "https://www.nytimes.com/by/david-e-sanger",
        "https://www.cnn.com/2026/02/18/politics/witkoff-kushner-iran-ukraine-geneva-analysis",
        "https://abcnews.com/International/witkoff-kushner-geneva-pivotal-talks-ukraine-iran/story?id=130223989",
        "https://www.moneycontrol.com/world/why-trump-is-relying-on-dealmakers-not-diplomats-in-talks-with-iran-and-russia-article-13833601.html",
        "https://www.nytimes.com/topic/subject/international-relations",
        "https://www.nytimes.com/spotlight/donald-trump"
      ],
      "hallucination_check": "Pass"
    }
  ]
}
