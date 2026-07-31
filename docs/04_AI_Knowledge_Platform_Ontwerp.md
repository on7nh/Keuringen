# AI & Knowledge Platform Ontwerp

## Digitaal Keurings- en Documentbeheer

**Versie:** 0.1 Concept  
**Status:** Eerste hoofdontwerp

## 1. Doel

Dit document beschrijft de centrale lokale AI- en kennislaag van het platform. De AI-omgeving wordt niet opgevat als één documentanalyseservice, maar als een uitbreidbaar intern AI-platform dat door het keurings- en documentbeheersysteem en later ook door andere interne toepassingen kan worden gebruikt.

Alle documenten, metadata, embeddings, prompts, correcties, modellen, evaluatiesets en trainingsgegevens blijven binnen de lokale infrastructuur.

## 2. Doelstellingen

- Lokale OCR-, vision- en taalmodelverwerking
- Automatische documentclassificatie en metadata-extractie
- Opbouw van een gecontroleerde technische kennisbank
- Inhoudelijk en semantisch zoeken in documenten
- Leren uit door gebruikers bevestigde correcties
- Versiebeheer van modellen, prompts en kennisregels
- Meetbare evaluatie vóór productieactivatie
- Mogelijkheid tot lokale LoRA- of QLoRA-fine-tuning
- Hergebruik van de AI-laag door toekomstige interne toepassingen

## 3. Beschikbare AI-infrastructuur

Voor het platform is volgende lokale AI-server voorzien:

- Serverplatform: HPE ProLiant ML350
- Werkgeheugen: 346 GiB RAM
- GPU's: 3 x NVIDIA GeForce RTX 3090
- GPU-geheugen: 24 GB VRAM per GPU, 72 GB totaal
- Initiële processors: 2 x Intel Xeon Silver 4110
- Geplande processorupgrade: Intel Xeon Gold 6258R

De architectuur wordt onafhankelijk gemaakt van het specifieke processortype. De geplande CPU-upgrade mag geen functionele aanpassingen aan de applicatie vereisen.

## 4. Platformarchitectuur

```text
Applicaties
   |
   +--> Keurings- en documentbeheer
   +--> Toekomstige interne toepassingen
   |
   v
Interne AI API / Gateway
   |
   +--> OCR Service
   +--> Vision Service
   +--> Language Model Service
   +--> Embedding Service
   +--> Knowledge Service
   +--> Evaluation Service
   +--> Training Service
   +--> Monitoring Service
```

De kernapplicatie communiceert uitsluitend via stabiele interne API's met het AI-platform. Daardoor kunnen modellen en uitvoeringsengines worden vervangen zonder de bedrijfslogica te herschrijven.

## 5. Logische diensten

### 5.1 OCR Service

- Tekstextractie uit gescande PDF's en afbeeldingen
- Taal- en paginadetectie
- Positie-informatie per tekstblok waar beschikbaar
- Betrouwbaarheidsscores
- Voorverwerking zoals rotatiecorrectie en beeldverbetering

### 5.2 Vision Service

- Analyse van documenten waarbij gewone tekstextractie onvoldoende is
- Interpretatie van formulieren, tabellen, stempels en visuele aanduidingen
- Toekomstige analyse en vergelijking van technische foto's

### 5.3 Language Model Service

- Documentclassificatie
- Extractie van Site, discipline, datums, status en opmerkingen
- Samenvattingen
- Vraag-en-antwoord op basis van lokale bronnen
- Gestructureerde JSON-output volgens versieerbare schema's

### 5.4 Embedding Service

- Lokale vectorrepresentatie van documentfragmenten
- Indexering van documenten en kennisobjecten
- Semantisch zoeken
- Detectie van inhoudelijk vergelijkbare documenten

### 5.5 Knowledge Service

- Beheer van goedgekeurde koppelingen en herkenningsregels
- Zoeken in relationele metadata en vectorindexen
- Samenstellen van relevante context voor AI-analyse
- Bronverwijzingen en herleidbaarheid van antwoorden

### 5.6 Evaluation Service

- Testen van modellen, prompts en regels op vaste datasets
- Vergelijking met de huidige productieversie
- Rapportage per veld, documenttype, model en promptversie

### 5.7 Training Service

- Export van gecontroleerde trainingsdata
- LoRA- en QLoRA-experimenten
- Beheer van adapters en checkpoints
- Geen automatische productieactivatie

### 5.8 Monitoring Service

- GPU-belasting, temperatuur en VRAM
- CPU-, RAM- en opslaggebruik
- Modelbeschikbaarheid
- Jobwachtrijen en verwerkingstijden
- Technische fouten en inhoudelijke kwaliteitsindicatoren

## 6. Centrale technische kennisbank

De kennisbank bevat niet alleen documenten, maar ook expliciete relaties tussen technische entiteiten.

Voorbeelden:

- Site en sitenummer
- Cabine en installatie
- EAN-nummer
- Organisatie
- Discipline
- Keuringsinstantie
- AREI-artikel
- Keuringsverslag
- Risicoanalyse
- Schema
- Handleiding
- Foto
- Opmerking of gebrek

Voorbeeld van een bevestigde kennisrelatie:

```text
"CABINE K34"
   -> Site Gent Zuid
   -> Discipline Hoogspanning
```

Iedere kennisrelatie bewaart minimaal de bron, de bevestigingsstatus, de gebruiker, het tijdstip en de geldigheidsperiode indien van toepassing.

## 7. Van document naar kennis

```text
Upload
  -> technische validatie
  -> tekstextractie of OCR
  -> documentclassificatie
  -> metadata-extractie
  -> manuele bevestiging
  -> fragmentering
  -> embeddings
  -> vectorindex
  -> kennisrelaties
  -> beschikbaar voor zoeken en RAG
```

Een document wordt pas als betrouwbare kennisbron gebruikt nadat de vereiste metadata en AI-resultaten zijn bevestigd.

## 8. Intelligente zoekfunctie

De zoekfunctie combineert:

- Klassieke filters op metadata
- Volledige tekstzoeking
- Semantische vectorzoeking
- Zoeken op relaties in de kennisbank
- Hybride rangschikking

Voorbeelden van ondersteunde vragen:

- Welke laagspanningskeuringen verlopen binnen drie maanden?
- Toon alle foto's van cabine K34.
- Welke installaties werden ooit afgekeurd wegens isolatiefout?
- Welke documenten verwijzen naar een bepaald AREI-artikel?
- Welke opmerkingen komen het vaakst terug?
- Welke documenten ontbreken voor deze Site?

Antwoorden moeten bronverwijzingen bevatten naar de gebruikte documenten en relevante passages.

## 9. Retrieval-Augmented Generation

Voor iedere kennisvraag of nieuwe documentanalyse wordt alleen relevante lokale context opgehaald.

```text
Vraag of document
  -> metadatafilters
  -> vectorzoeking
  -> kennisregels
  -> reranking
  -> beperkte contextselectie
  -> lokaal taalmodel
  -> antwoord of voorstel met bronnen
```

De eerste versie kan PostgreSQL met pgvector gebruiken. Een afzonderlijke vectordatabase blijft mogelijk wanneer schaal of beheer dit later vereist.

## 10. Leren uit menselijke correcties

### 10.1 Feedbackregistratie

Per correctie worden minimaal opgeslagen:

- Document en documenttype
- Gecorrigeerd veld
- AI-voorstel
- Definitief bevestigde waarde
- Betrouwbaarheidsscore
- Model- en promptversie
- Gebruiker en tijdstip
- Reden of opmerking, indien ingevuld

### 10.2 Kennisregels

Eenduidige, terugkerende correcties kunnen worden omgezet in goedgekeurde kennisregels, zoals:

- cabinecode naar Site
- vaste benaming naar installatie
- afkorting naar discipline
- formulering naar keuringsstatus

Een regel wordt pas actief na expliciete goedkeuring of nadat een configureerbare bevestigingsdrempel is bereikt en een bevoegde gebruiker de regel heeft beoordeeld.

### 10.3 Voorbeelden in de prompt

Relevante, eerder bevestigde voorbeelden kunnen automatisch worden toegevoegd aan de analysecontext. Hierdoor verbetert de herkenning zonder dat het basismodel direct opnieuw wordt getraind.

### 10.4 Fine-tuning

Wanneer voldoende kwalitatieve correcties beschikbaar zijn, kunnen deze worden gebruikt voor gecontroleerde LoRA- of QLoRA-fine-tuning. Volledige training van een groot taalmodel vanaf nul valt buiten de scope.

## 11. GPU- en capaciteitsbeheer

De GPU-verdeling wordt configureerbaar en niet hard gecodeerd.

Eerste uitgangspunt:

- GPU 0: productie-inferentie voor taalmodellen
- GPU 1: vision en GPU-versnelde OCR
- GPU 2: tweede inferentiewerker, evaluatie, batchverwerking en gecontroleerde training

Het platform ondersteunt later ook modelparallelisme over meerdere GPU's wanneer een model niet binnen 24 GB VRAM past.

Prioriteitsregels:

- Interactieve productiejobs krijgen voorrang
- Training en grote evaluaties draaien bij voorkeur buiten werkuren
- Grote batchuploads mogen normale verwerking niet blokkeren
- Jobs blijven veilig in de wachtrij bij onvoldoende capaciteit
- Per GPU en model wordt een maximum aantal gelijktijdige jobs ingesteld

## 12. Model- en promptbeheer

Per model worden minimaal bijgehouden:

- Interne naam en modelfamilie
- Modelidentifier en versie
- Type: tekst, vision, OCR, embedding of reranker
- Quantisatie
- Benodigde GPU's en verwacht VRAM-gebruik
- Contextlengte
- Ondersteunde jobtypes
- API-endpoint
- Timeout en retries
- Productie-, test- of trainingsstatus
- Checksum van de gebruikte bestanden

Per prompt worden minimaal bijgehouden:

- Naam en versie
- Doel en documenttype
- Instructies en outputschema
- Datum van activatie
- Goedkeurder
- Evaluatieresultaten

## 13. Evaluatie en productiepromotie

Nieuwe modellen, prompts en kennisregels doorlopen:

1. Registratie als nieuwe versie
2. Test op een vaste gevalideerde dataset
3. Meting per veld en documenttype
4. Vergelijking met de productieversie
5. Manuele goedkeuring
6. Gefaseerde activatie
7. Monitoring
8. Rollback bij slechtere resultaten

Belangrijke kwaliteitsindicatoren:

- Exacte nauwkeurigheid per veld
- Correctiepercentage
- Percentage volledig ongewijzigd bevestigde documenten
- Antwoordkwaliteit en bronjuistheid
- Verwerkingstijd
- Foutpercentage
- Wachttijd
- GPU- en VRAM-gebruik

## 14. Beveiliging en privacy

- Geen documenten of metadata naar externe AI-diensten
- AI API alleen bereikbaar voor toegestane interne services
- Authenticatie en versleuteling van intern API-verkeer
- Geen publieke rechtstreekse toegang tot modelservers
- Strikte rechten op trainingsdata en evaluatiesets
- Geen onbeperkte opslag van ruwe prompts of documenten in technische logs
- Volledige audit van model-, prompt-, regel- en kenniswijzigingen
- Bescherming tegen promptinjectie in documenten en kennisbronnen

## 15. Opslag en back-up

- Productiemodellen op lokale snelle opslag
- Trainings- en evaluatiesets logisch gescheiden
- Correcties, kennisregels en modelmetadata in PostgreSQL
- Embeddings in PostgreSQL/pgvector of een lokale vectordatabase
- Back-up van eigen adapters, prompts, configuraties en evaluatieresultaten
- Registratie van exacte basismodelversies en checksums
- PostgreSQL-back-up naar de Synology NAS volgens het algemene back-upbeleid

## 16. Toekomstige uitbreidingen

Het AI-platform wordt voorbereid op:

- Interne technische assistent
- Automatische samenvattingen per Site of installatie
- Detectie van ontbrekende documenten
- Analyse van terugkerende gebreken
- Ondersteuning van risicoanalyses
- E-mailanalyse en automatische classificatie
- Technische rapportgeneratie
- Vergelijking van technische foto's
- Predictive maintenance op basis van voldoende betrouwbare historische data
- Hergebruik door ERP-, onderhouds- en andere interne toepassingen

## 17. Openstaande keuzes

- Linuxdistributie en containerstrategie voor GPU-workloads
- Modelserver voor tekst- en visionmodellen
- OCR-engine
- Eerste productie-LLM, visionmodel, embeddingmodel en reranker
- pgvector of afzonderlijke vectordatabase
- Opslagcapaciteit voor modellen, datasets en vectorindexen
- Drempel en goedkeuringsworkflow voor automatische kennisregels
- Scheiding tussen productie-, test- en trainingsomgevingen
- Monitoringstack
