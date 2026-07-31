# UI/UX-ontwerp Toestellenmodule

## Digitaal Keurings- en Documentbeheer

**Documentnummer:** 12  
**Versie:** 1.0 Concept  
**Gerelateerd:** `07_UI_UX_Ontwerp.md`, `09_Toestellen_En_Onderhoudsbeheer.md`, `11_API_Ontwerp_Toestellen.md`

## 1. Doel

Dit document beschrijft de gebruikerservaring, schermstructuur, interactiepatronen, responsive werking en toegankelijkheid van de toestellen- en onderhoudsmodule.

De module ondersteunt zowel desktopgebruik door beheerders als mobiel gebruik door techniekers en medewerkers die een QR-code scannen.

## 2. UX-principes

- Mobile-first voor QR, onderhoud, storingen en keuringen.
- Desktop-first voor beheer, rapportage, configuratie en bulkacties.
- Taken staan centraal, niet de onderliggende databasemodellen.
- Status en urgentie zijn onmiddellijk zichtbaar.
- Kritieke acties vereisen expliciete bevestiging.
- De gebruiker ziet alleen functies waarvoor hij bevoegd is.
- Formulieren bewaren concepten automatisch.
- Alle processen zijn hervatbaar na netwerkverlies.
- Geen cruciale informatie uitsluitend via kleur communiceren.
- Sneltoetsen en toetsenbordnavigatie worden ondersteund.

## 3. Primaire gebruikersrollen

### 3.1 Organisatiebeheerder

Beheert stamgegevens, rechten, rapporten, imports, QR-labels en organisatiebrede configuratie.

### 3.2 Site Facility Manager

Beheert toestellen, locaties, onderhoudsplanning, storingen, herstellingen en keuringen binnen één of meer sites.

### 3.3 Technieker

Ontvangt opdrachten, scant QR-codes, registreert werkzaamheden, voegt foto's toe en rondt taken af.

### 3.4 Franchisee of siteverantwoordelijke

Raadpleegt toestellen, meldt storingen, bevestigt onderhoud en volgt compliance op.

### 3.5 Keurder

Voert keuringen uit, registreert bevindingen en voegt attesten toe.

### 3.6 Lezer of auditor

Heeft alleen-lezen toegang tot historiek, documenten, keuringen en rapporten.

## 4. Informatiearchitectuur

Hoofdnavigatie:

```text
Dashboard
Toestellen
Onderhoud
Storingen
Herstellingen
Keuringen
Documenten
Rapporten
Configuratie
```

Onder `Toestellen`:

```text
Alle toestellen
Mijn sites
Kaart / locaties
QR-labels
Import
Archief
```

## 5. Globale layout

Desktop:

```text
+-------------------------------------------------------------+
| Logo | Zoekbalk | Sitefilter | Meldingen | Profiel          |
+----------------------+--------------------------------------+
| Navigatie            | Pagina-inhoud                        |
|                      |                                      |
|                      |                                      |
+----------------------+--------------------------------------+
```

Mobiel:

```text
+-----------------------------------+
| Terug | Titel | Acties            |
+-----------------------------------+
| Inhoud                            |
|                                   |
+-----------------------------------+
| Home | Taken | Scan | Meldingen   |
+-----------------------------------+
```

De mobiele navigatie bevat een prominente scanactie in het midden.

## 6. Dashboard

### 6.1 Organisatiedashboard

KPI-kaarten:

- totaal aantal actieve toestellen;
- toestellen met open storing;
- achterstallig onderhoud;
- keuringen die binnen 30 dagen vervallen;
- afgekeurde toestellen;
- gemiddelde hersteltijd;
- onderhoudscompliance;
- kosten huidige periode.

Grafieken:

- storingen per maand;
- onderhoud uitgevoerd versus gepland;
- kosten per site;
- storingen per categorie;
- top tien toestellen met meeste uitval;
- keuringstatus per organisatie-eenheid.

### 6.2 Persoonlijk dashboard

Toont:

- mijn open taken;
- vandaag gepland onderhoud;
- urgente storingen;
- te bevestigen werkzaamheden;
- recente QR-scans;
- conceptregistraties;
- meldingen waarvoor actie vereist is.

### 6.3 Dashboardfilters

Globale filters:

- organisatie;
- site;
- periode;
- categorie;
- type;
- merk;
- status;
- kriticiteit.

Filters blijven gedurende de sessie behouden.

## 7. Toestellenoverzicht

### 7.1 Desktoplijst

Kolommen:

- toestelcode;
- naam;
- site;
- locatie;
- type;
- merk/model;
- status;
- open storingen;
- volgend onderhoud;
- volgende keuring;
- verantwoordelijke;
- acties.

Functies:

- sorteren;
- kolommen tonen/verbergen;
- opgeslagen filters;
- exporteren;
- bulkselectie;
- snelle statusfilter;
- vrije zoekterm;
- zoeken op serienummer, inventarisnummer en toestelcode.

### 7.2 Kaartweergave

Voor organisaties met geografisch verspreide sites:

- marker per site;
- kleur en pictogram op basis van risicostatus;
- clustering;
- filter op toesteltype en storingsstatus;
- doorklik naar siteoverzicht.

### 7.3 Mobiele kaartweergave

Mobiel worden compacte kaarten gebruikt met:

- naam;
- toestelcode;
- locatie;
- statuschip;
- eerstvolgende actie;
- snelknoppen voor details, storing en scan.

## 8. Nieuw toestel-wizard

De wizard bestaat uit maximaal zes stappen.

### Stap 1 — Organisatie en locatie

- organisatie;
- site;
- gebouw;
- verdieping;
- ruimte;
- verantwoordelijke.

### Stap 2 — Classificatie

- toesteltype;
- categorie;
- merk;
- model;
- eigen naam;
- serienummer;
- inventarisnummer.

Bij keuze van model worden standaardwaarden automatisch ingevuld.

### Stap 3 — Technische gegevens

Dynamische velden afhankelijk van toesteltype, bijvoorbeeld:

- vermogen;
- spanning;
- koelmiddel;
- capaciteit;
- bouwjaar;
- veiligheidsklasse.

### Stap 4 — Aankoop en garantie

- leverancier;
- aankoopdatum;
- aankoopprijs;
- ingebruiknamedatum;
- garantiedatum;
- factuur koppelen.

### Stap 5 — Onderhoud en keuring

- onderhoudsplan;
- eerste onderhoudsdatum;
- keuringsplan;
- eerste keuringsdatum;
- kriticiteit.

### Stap 6 — Documenten en QR

- foto's uploaden;
- handleiding koppelen;
- plannen koppelen;
- QR-label genereren;
- samenvatting en bevestiging.

De wizard ondersteunt:

- tussentijds bewaren;
- terugkeren zonder gegevensverlies;
- veldvalidatie per stap;
- waarschuwing bij vermoedelijke duplicaten;
- overzicht van automatisch overgenomen modelgegevens.

## 9. Toesteldetailpagina

Header:

- toestelnaam;
- toestelcode;
- status;
- kriticiteit;
- site en locatie;
- primaire acties.

Tabbladen:

```text
Overzicht
Tijdlijn
Onderhoud
Storingen
Herstellingen
Keuringen
Documenten
Foto's
Statistieken
QR-labels
Instellingen
```

### 9.1 Overzicht

Toont:

- hoofdafbeelding;
- kerngegevens;
- verantwoordelijke;
- volgende onderhoudsdatum;
- volgende keuringsdatum;
- open storingen;
- garantie;
- recente gebeurtenissen;
- snelacties.

### 9.2 Tijdlijn

Chronologische gebeurtenissen met filters voor:

- onderhoud;
- storing;
- herstelling;
- keuring;
- statuswijziging;
- locatieverplaatsing;
- document;
- QR-label.

### 9.3 Statistieken

KPI's en grafieken voor geselecteerde periode:

- aantal storingen;
- totale stilstand;
- MTTR;
- MTBF;
- onderhoudskosten;
- herstellingskosten;
- compliance;
- trend ten opzichte van vorige periode.

## 10. QR-landingspagina

De QR-landingspagina is geoptimaliseerd voor gebruik met één hand.

Bovenaan:

- toestelnaam;
- toestelcode;
- duidelijke status;
- locatie;
- hoofdafbeelding.

Primaire acties:

- storing melden;
- onderhoud bekijken;
- onderhoud bevestigen;
- documentatie openen;
- contactpersoon bellen;
- route of locatie bekijken.

Voor niet-aangemelde gebruikers:

- minimale openbare informatie;
- geen serienummer, kosten of gevoelige documenten;
- mogelijkheid om aan te melden;
- eventueel beperkte storingsmelding volgens beleid.

Voor aangemelde techniekers:

- volledige taakcontext;
- open werkopdrachten;
- starten en afronden;
- foto's nemen;
- onderdelen registreren;
- metingen invoeren.

## 11. Onderhoudsoverzicht

Weergaven:

- lijst;
- kalender;
- weekplanning;
- techniekerplanning;
- sitesamenvatting.

Statuschips:

- gepland;
- toegewezen;
- gestart;
- voltooid;
- te bevestigen;
- achterstallig;
- geannuleerd;
- niet uitvoerbaar.

Drag-and-drop in planning is toegestaan voor bevoegde planners, met bevestigingsdialoog bij datum- of techniekerwijziging.

## 12. Onderhoud uitvoeren

Mobiele flow:

1. QR scannen of taak openen.
2. Controle toestelidentiteit.
3. Taak starten.
4. Checklist doorlopen.
5. Metingen registreren.
6. Foto's toevoegen.
7. Afwijkingen registreren.
8. Onderdelen en werktijd invoeren.
9. Resultaat kiezen.
10. Volgende vervaldatum bevestigen.
11. Digitaal ondertekenen of bevestigen.

Offline gedrag:

- formulier lokaal cachen;
- foto's in wachtrij plaatsen;
- duidelijke synchronisatiestatus;
- conflicten expliciet tonen;
- nooit stilzwijgend overschrijven.

## 13. Storingen

### 13.1 Storing melden

Minimale flow:

- toestel automatisch ingevuld;
- omschrijving;
- impact;
- urgentie;
- toestel bruikbaar ja/nee;
- veiligheidsrisico ja/nee;
- foto of video;
- contactgegevens indien nodig.

Bij veiligheidsrisico verschijnt een prominente waarschuwing en worden organisatieprocedures getoond.

### 13.2 Storingenbord

Kanbanweergave:

```text
Nieuw | Getrieerd | Toegewezen | In uitvoering | Opgelost | Gesloten
```

Kaarten tonen:

- toestel;
- site;
- prioriteit;
- ouderdom;
- verantwoordelijke;
- SLA-status;
- veiligheidsindicator.

## 14. Herstellingen

Herstellingsformulier bevat:

- gekoppelde storingen;
- diagnose;
- hoofdoorzaak;
- uitgevoerde werkzaamheden;
- onderdelen;
- werkuren;
- externe leverancier;
- kosten;
- testresultaat;
- eindstatus;
- documenten en foto's.

Bij afronding vraagt de UI expliciet of:

- het toestel opnieuw in dienst mag;
- gekoppelde storingen mogen worden opgelost;
- vervolgonderhoud nodig is;
- een corrigerende actie moet worden aangemaakt.

## 15. Keuringen

Keuringsoverzicht bevat:

- te plannen;
- gepland;
- binnenkort vervallend;
- vervallen;
- afgekeurd;
- goedgekeurd met opmerkingen.

De keuringsflow ondersteunt:

- keuringschecklist;
- norm of referentie;
- metingen;
- bevindingen;
- ernst;
- foto's;
- hersteltermijn;
- attestupload;
- digitale bevestiging.

Bij afkeuring wordt de gebruiker gevraagd het toestel direct buiten dienst te plaatsen.

## 16. Documenten en foto's

Documentcategorieën:

- handleiding;
- plan;
- attest;
- factuur;
- werkbon;
- foto;
- keuringsrapport;
- certificaat;
- overige bijlage.

Functies:

- drag-and-drop;
- camera-upload;
- versiehistoriek;
- voorvertoning;
- geldigheidsdatum;
- document als hoofdhandleiding markeren;
- OCR-status tonen;
- AI-samenvatting openen;
- rechten per document respecteren.

## 17. QR-labelbeheer

Schermen:

- actieve labels;
- ingetrokken labels;
- printwachtrij;
- bulklabelgeneratie;
- labelvoorbeeld;
- scanstatistieken.

Acties:

- nieuw label genereren;
- label opnieuw afdrukken;
- label vervangen;
- label intrekken;
- reden registreren;
- printerformaat kiezen.

## 18. Rapporten

Rapportpagina's:

- organisatieoverzicht;
- sitevergelijking;
- storingsanalyse;
- betrouwbaarheid;
- onderhoudscompliance;
- keuringscompliance;
- kostenanalyse;
- vervangingsplanning;
- toestelhistoriek.

Elk rapport bevat:

- filters;
- KPI-kaarten;
- grafieken;
- detailtabel;
- drill-down;
- export;
- definitie van berekende indicatoren.

## 19. Bulkacties

Beschikbare bulkacties:

- verplaatsen;
- verantwoordelijke wijzigen;
- onderhoudsplan toekennen;
- keuringsplan toekennen;
- QR-labels genereren;
- archiveren;
- exporteren.

Voor uitvoering toont de UI:

- aantal geselecteerde toestellen;
- simulatie;
- waarschuwingen;
- blokkerende fouten;
- bevestiging;
- voortgang;
- resultaatrapport.

## 20. Importwizard

Stappen:

1. Bestand uploaden.
2. Werkblad kiezen.
3. Kolommen koppelen.
4. Waarden normaliseren.
5. Duplicaten controleren.
6. Validatie uitvoeren.
7. Simulatie bekijken.
8. Import starten.
9. Resultaten en fouten downloaden.

De wizard ondersteunt hervatten en bewaart de gekozen mapping als sjabloon.

## 21. Meldingen

Meldingstypen:

- onderhoud binnenkort vervallen;
- onderhoud achterstallig;
- nieuwe storing;
- storing toegewezen;
- keuring binnenkort vervallen;
- toestel afgekeurd;
- werk te bevestigen;
- export voltooid;
- import met fouten;
- synchronisatieconflict.

Meldingen linken rechtstreeks naar de relevante taak of entiteit.

## 22. Statusweergave

Elke status gebruikt een combinatie van:

- tekstlabel;
- pictogram;
- kleur;
- eventueel urgentie-indicator.

Voorbeelden:

- Actief — vinkpictogram.
- Storing — waarschuwingsdriehoek.
- Buiten dienst — stop-pictogram.
- Afgekeurd — schild met kruis.
- Onderhoud vervallen — klok met waarschuwing.

## 23. Formuliervalidatie

Validatie gebeurt:

- direct waar veilig;
- bij verlaten van veld;
- bij stapovergang;
- opnieuw server-side bij opslaan.

Foutmeldingen zijn specifiek en handelingsgericht.

Slecht:

```text
Ongeldige invoer
```

Goed:

```text
De keuringsdatum moet vóór de vervaldatum liggen.
```

## 24. Bevestigingspatronen

Een extra bevestiging is vereist voor:

- archiveren;
- buiten dienst plaatsen;
- toestel opnieuw in dienst nemen;
- QR-label intrekken;
- storing sluiten;
- keuring definitief afronden;
- bulkacties;
- import uitvoeren.

Voor acties met hoge impact kan step-up authenticatie worden gevraagd.

## 25. Zoekervaring

Globale zoekfunctie ondersteunt:

- toestelcode;
- naam;
- serienummer;
- inventarisnummer;
- merk;
- model;
- site;
- ruimte;
- documentinhoud via OCR/RAG waar toegestaan.

Resultaten worden per categorie gegroepeerd.

## 26. Toegankelijkheid

Doel: minimaal WCAG 2.2 AA.

Vereisten:

- volledige toetsenbordbediening;
- zichtbare focus;
- juiste semantische HTML;
- labels voor alle velden;
- foutmeldingen gekoppeld aan velden;
- voldoende contrast;
- schermlezerteksten voor pictogrammen;
- grafiekdata ook in tabelvorm;
- geen tijdslimiet zonder verlengoptie;
- touch targets minimaal 44 bij 44 CSS-pixels.

## 27. Responsive breakpoints

Aanbevolen:

- mobiel: kleiner dan 768 px;
- tablet: 768–1199 px;
- desktop: 1200 px en groter.

Tabellen schakelen op mobiel om naar kaarten, tenzij horizontaal vergelijken noodzakelijk is.

## 28. Offline en slechte verbinding

De mobiele interface toont altijd één van deze statussen:

- online;
- offline;
- synchroniseren;
- synchronisatie mislukt;
- conflict vereist actie.

Acties die servervalidatie vereisen worden als voorlopig gemarkeerd totdat synchronisatie geslaagd is.

## 29. Prestatie-eisen

- Eerste bruikbare mobiele weergave binnen 2,5 seconden op normaal 4G-netwerk.
- QR-resolutie en eerste toestelsamenvatting binnen 1,5 seconde onder normale belasting.
- Lijsten gebruiken virtualisatie vanaf grote aantallen.
- Afbeeldingen worden als thumbnails geladen.
- Grafieken worden pas geladen wanneer zichtbaar.
- Filters worden gedebounced.

## 30. Componentenbibliotheek

Belangrijke herbruikbare componenten:

- `AssetStatusChip`
- `AssetSummaryCard`
- `LocationBreadcrumb`
- `QrScanButton`
- `MaintenanceChecklist`
- `FaultPriorityBadge`
- `InspectionResultBadge`
- `DocumentPreviewCard`
- `TimelineEvent`
- `MetricCard`
- `FilterBar`
- `OfflineSyncIndicator`
- `BulkActionDialog`
- `StepUpAuthenticationDialog`

## 31. Analytics en UX-metingen

Te meten zonder onnodige persoonsgegevens:

- tijd tot toestel gevonden;
- tijd tot storing gemeld;
- voltooiingsgraad onderhoudsflow;
- formulieruitval per stap;
- aantal scanpogingen;
- foutfrequentie per workflow;
- offline synchronisatieproblemen;
- gebruik van filters en opgeslagen weergaven.

## 32. Wireframe — QR-landingspagina

```text
+----------------------------------+
| Koelcel keuken 1                 |
| SITE_00001247 · AST-000184       |
| [ STORING ]                      |
+----------------------------------+
| Foto                             |
| Locatie: Keuken / Koelruimte     |
| Volgend onderhoud: 12 aug 2026   |
| Volgende keuring: 04 nov 2026    |
+----------------------------------+
| [ Storing melden ]               |
| [ Onderhoud bekijken ]           |
| [ Documentatie ]                 |
| [ Meer details ]                 |
+----------------------------------+
```

## 33. Wireframe — toesteldetail desktop

```text
+----------------------------------------------------------------+
| Koelcel keuken 1     [Storing] [Bewerken] [Meer]                |
| AST-000184 · Site Brussel · Keuken / Koelruimte                 |
+----------------------------------------------------------------+
| Overzicht | Tijdlijn | Onderhoud | Storingen | Keuringen | ... |
+----------------------------------------------------------------+
| Kerngegevens           | Open acties                            |
| Merk / Model           | 1 urgente storing                      |
| Serienummer            | Onderhoud 12 dagen vervallen           |
| Verantwoordelijke      | Keuring binnen 45 dagen                |
+----------------------------------------------------------------+
| Recente gebeurtenissen                                        |
+----------------------------------------------------------------+
```

## 34. Acceptatiecriteria

- Alle kernflows werken op mobiel, tablet en desktop.
- QR-flow vereist maximaal twee interacties voor storing melden.
- Een technieker kan onderhoud volledig mobiel uitvoeren.
- Concepten gaan niet verloren bij netwerkonderbreking.
- Elke kritieke actie heeft passende bevestiging.
- Gebruikers zien uitsluitend toegestane acties en data.
- Status is nooit alleen via kleur herkenbaar.
- Rapporten ondersteunen drill-down en export.
- De UI voldoet aan WCAG 2.2 AA voor kernprocessen.
- Componenten en statussen zijn consistent met het algemene UI/UX-ontwerp.
