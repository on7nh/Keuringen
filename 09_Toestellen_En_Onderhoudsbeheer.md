# Ontwerp Toestellen- en Onderhoudsbeheer

## Digitaal Keurings- en Documentbeheer

**Documentnummer:** 09  
**Versie:** 1.0 Concept  
**Status:** Nieuwe functionele module  
**Repository:** `on7nh/Keuringen`

## 1. Doel

Deze module maakt het mogelijk om toestellen, machines, installaties en andere bedrijfsmiddelen binnen een organisatie te registreren, te classificeren en gedurende hun volledige levenscyclus op te volgen.

Elk toestel krijgt een uniek toestelnummer en kan aan een fysieke QR-code worden gekoppeld. Na het scannen van de QR-code komt de gebruiker op de landingspagina van het toestel.

Vanaf deze pagina kunnen bevoegde gebruikers onder andere:

- toestelgegevens raadplegen;
- een onderhoud registreren of bevestigen;
- een storing melden;
- een herstelling registreren;
- een keuring registreren;
- opmerkingen en meetgegevens toevoegen;
- foto's uploaden;
- handleidingen en technische plannen raadplegen;
- de volledige historie bekijken.

Site Facility Managers en franchisees krijgen overzichts- en rapporteringsmogelijkheden over hun toegestane sites en organisaties.

## 2. Terminologie

In dit document wordt de overkoepelende term **toestel** gebruikt.

Een toestel kan onder meer zijn:

- machine;
- elektrisch apparaat;
- koelinstallatie;
- HVAC-installatie;
- keukenapparaat;
- brandveiligheidsmiddel;
- lift;
- voertuiggebonden installatie;
- meetinstrument;
- IT- of netwerktoestel;
- onderdeel van een vaste technische installatie.

De organisatie kan zelf soorten, categorieën en classificaties beheren.

## 3. Organisatiestructuur en eigenaarschap

Een toestel behoort altijd tot precies één organisatie.

Een toestel kan optioneel gekoppeld zijn aan:

- één site;
- één gebouw;
- één verdieping;
- één ruimte of zone;
- één functionele installatie;
- één kostenplaats;
- één verantwoordelijke dienst;
- één externe onderhoudspartner.

Een toestel kan tijdens zijn levenscyclus worden verplaatst. Verplaatsingen worden historisch geregistreerd en overschrijven de vroegere locatie niet zonder auditspoor.

## 4. Rollen en rechten

### 4.1 Site Facility Manager

De Site Facility Manager kan binnen de toegewezen sites:

- toestellen bekijken;
- toestellen registreren;
- toestelgegevens wijzigen;
- QR-codes genereren en opnieuw afdrukken;
- onderhoud, herstellingen en keuringen registreren;
- documenten en foto's toevoegen;
- rapporten en statistieken bekijken;
- geplande acties opvolgen;
- defecte of buiten dienst gestelde toestellen opvolgen.

### 4.2 Franchisee

De franchisee kan binnen de toegewezen organisatie of franchisestructuur:

- organisatiewijde overzichten bekijken;
- sites vergelijken;
- toestelstatistieken bekijken;
- onderhoudsachterstanden opvolgen;
- storingsfrequenties en kosten analyseren;
- exporten uitvoeren voor rapportering.

De franchisee kan alleen gegevens wijzigen wanneer dit via de autorisatiematrix expliciet is toegestaan.

### 4.3 Technieker of onderhoudspartner

Een interne of externe technieker kan, afhankelijk van de toegekende rechten:

- een QR-code scannen;
- de beperkte toestelpagina bekijken;
- onderhoud bevestigen;
- een herstelling registreren;
- foto's en werkbonnen toevoegen;
- gebruikte onderdelen en werkuren registreren;
- een interventie afsluiten.

### 4.4 Organisatiebeheerder

De organisatiebeheerder beheert:

- toestelsoorten;
- categorieën;
- merken;
- modellen;
- onderhoudstypes;
- storingscodes;
- keuringsschema's;
- verplichte velden;
- toegangsrechten;
- bewaartermijnen;
- rapportage-instellingen.

## 5. Toestelclassificatie

Een toestel moet minstens geclassificeerd kunnen worden volgens:

- organisatie;
- site;
- merk;
- model;
- soort;
- categorie;
- subcategorie;
- serienummer;
- intern inventarisnummer;
- status;
- criticiteitsniveau;
- installatie- of ingebruiknamedatum.

Optionele kenmerken:

- fabrikant;
- leverancier;
- bouwjaar;
- aankoopdatum;
- garantie-einddatum;
- kostprijs;
- vermogen;
- spanning;
- brandstof- of energietype;
- CE-markering;
- keuringsplicht;
- onderhoudsinterval;
- expected lifetime;
- technische kenmerken als configureerbare velden;
- locatiecoördinaten of ruimtecode.

### 5.1 Stamgegevens

Merken, soorten, categorieën en modellen worden als beheerde stamgegevens opgeslagen.

Hierdoor ontstaan consistente rapporten. Vrije tekst voor merk of soort wordt vermeden, behalve tijdens gecontroleerde import waarbij later normalisatie wordt uitgevoerd.

### 5.2 Organisatiespecifieke classificatie

Elke organisatie kan eigen classificaties toevoegen, maar centrale categorieën kunnen als standaardcatalogus worden aangeboden.

Een organisatie kan bijvoorbeeld zelf toestelsoorten definiëren zoals:

- friteuse;
- koelcel;
- koffiemachine;
- luchtgroep;
- brandblusser;
- elektrische verdeelkast.

## 6. Uniek toestelnummer

Elk toestel krijgt een onveranderlijk intern toestelnummer.

Voorbeeld:

```text
AST_000001247
```

Het toestelnummer:

- is uniek over het volledige platform;
- verandert niet bij een wijziging van naam, site of organisatie-eigenschappen;
- wordt gebruikt in auditlogs en QR-resolutie;
- is niet afhankelijk van merk, soort of locatie;
- wordt toegekend door de centrale Naming Service.

Een mensvriendelijke weergavenaam kan wel worden aangepast.

## 7. Toestelstatus

Ondersteunde standaardstatussen:

- concept;
- actief;
- onderhoud gepland;
- defect;
- beperkte werking;
- buiten dienst;
- in herstelling;
- afgekeurd;
- verkocht of overgedragen;
- verwijderd uit inventaris;
- gearchiveerd.

Statuswijzigingen worden als gebeurtenissen opgeslagen met:

- vorige status;
- nieuwe status;
- datum en tijd;
- uitvoerende gebruiker;
- reden;
- eventuele bijlage;
- bron van de wijziging.

## 8. QR-code

### 8.1 Koppeling

Bij het aanmaken van een toestel kan automatisch een QR-code worden gegenereerd.

De QR-code bevat geen gevoelige toestelgegevens. De code bevat alleen een URL met een onvoorspelbare publieke identifier of resolver-token.

Voorbeeld:

```text
https://keuringen.intern.example/q/a8F3kP2xQm7L
```

De QR-code bevat niet rechtstreeks:

- toestelnaam;
- serienummer;
- organisatie-id;
- site-id;
- interne database-id;
- persoonsgegevens;
- toegangsrechten.

### 8.2 QR-identiteit

Een toestel kan meerdere QR-labels krijgen, bijvoorbeeld:

- primair label;
- vervanglabel;
- label op binnen- en buitenzijde;
- label per toegankelijk onderhoudspunt.

Elk label heeft:

- een unieke token;
- creatiedatum;
- status;
- afdrukdatum;
- optionele labelversie;
- laatste scandatum;
- aantal scans;
- reden van intrekking.

Een verloren of beschadigd label kan worden ingetrokken zonder het toestel te verwijderen.

### 8.3 QR-landingspagina

Na het scannen wordt de QR-token server-side opgelost naar het toestel.

De landingspagina toont afhankelijk van authenticatie en autorisatie:

**Zonder aanmelding of met beperkte externe toegang:**

- beperkte toestelnaam;
- site of locatie indien toegestaan;
- status;
- noodcontact of meldknop;
- mogelijkheid om een storing te melden;
- geen gevoelige documenten of volledige historie.

**Na aanmelding:**

- volledige toestelgegevens;
- documenten en foto's;
- onderhouds- en herstellingshistorie;
- keuringshistorie;
- geplande acties;
- statistieken;
- toegestane actieknoppen.

### 8.4 Beveiliging QR-flow

De QR-token moet:

- cryptografisch willekeurig zijn;
- voldoende entropie bevatten;
- niet sequentieel zijn;
- intrekbaar zijn;
- rate-limited worden opgevraagd;
- geen autorisatie vervangen.

Voor gevoelige acties moet de gebruiker aangemeld zijn. Voor kritieke acties kan step-up authenticatie verplicht zijn.

## 9. Toestellandingspagina

De toestelpagina bevat minimaal de volgende tabbladen.

### 9.1 Overzicht

- toestelnummer;
- naam;
- soort;
- categorie;
- merk en model;
- serienummer;
- actuele status;
- actuele locatie;
- verantwoordelijke;
- eerstvolgend onderhoud;
- eerstvolgende keuring;
- openstaande storingen;
- kriticiteit;
- hoofdafbeelding.

### 9.2 Historie

Chronologische tijdlijn van:

- registratie;
- locatieverplaatsingen;
- statuswijzigingen;
- onderhoud;
- storingen;
- herstellingen;
- keuringen;
- documentupdates;
- QR-labelwijzigingen;
- eigendomsoverdrachten.

### 9.3 Onderhoud

- gepland onderhoud;
- uitgevoerd onderhoud;
- onderhoudstype;
- uitvoerder;
- datum;
- duur;
- opmerkingen;
- checklist;
- gebruikte onderdelen;
- kosten;
- bijlagen;
- volgende onderhoudsdatum.

### 9.4 Storingen en herstellingen

- foutmelding;
- storingscode;
- prioriteit;
- impact;
- melder;
- datum en tijd melding;
- datum en tijd eerste reactie;
- datum en tijd herstel;
- oorzaak;
- oplossing;
- gebruikte onderdelen;
- werkuren;
- externe kosten;
- totale stilstand;
- herhaling van dezelfde storing;
- foto's voor en na herstelling.

### 9.5 Keuringen

- type keuring;
- keuringsinstantie;
- keuringsdatum;
- resultaat;
- vervaldatum;
- opmerkingen;
- tekortkomingen;
- herstelacties;
- keuringsattest;
- herinneringen.

### 9.6 Documenten

Ondersteunde documentcategorieën:

- handleiding;
- technisch plan;
- elektrisch schema;
- veiligheidsfiche;
- conformiteitsverklaring;
- aankoopdocument;
- garantiedocument;
- onderhoudsrapport;
- werkbon;
- keuringsattest;
- foto;
- video;
- overige bijlage.

Documenten gebruiken dezelfde documentbeheerprincipes als de rest van het platform:

- versiebeheer;
- immutable opslaglocatie;
- metadata;
- audit;
- toegangscontrole;
- OCR en AI-classificatie waar van toepassing.

## 10. Onderhoud registreren en bevestigen

Een onderhoudsregistratie kan ontstaan door:

- manuele registratie;
- een gepland onderhoudsschema;
- QR-scan;
- externe werkbon;
- API-import;
- automatische trigger op tellerstand of gebruiksuren.

Een onderhoud bevat minimaal:

- toestel;
- onderhoudstype;
- geplande datum;
- uitvoeringsdatum;
- uitvoerder;
- status;
- resultaat;
- opmerkingen;
- volgende onderhoudsdatum.

Onderhoudsstatussen:

- gepland;
- toegewezen;
- gestart;
- uitgevoerd;
- gedeeltelijk uitgevoerd;
- afgekeurd;
- geannuleerd;
- niet uitvoerbaar;
- bevestigd.

### 10.1 Bevestigingsflow via QR

1. Technieker scant QR-code.
2. Systeem opent toestelpagina.
3. Technieker meldt zich aan indien vereist.
4. Technieker kiest **Onderhoud bevestigen**.
5. Systeem toont openstaande onderhoudstaak.
6. Technieker vult checklist, opmerkingen, foto's en meetwaarden in.
7. Technieker bevestigt uitvoering.
8. Systeem registreert datum, gebruiker, toestel, locatie en auditgegevens.
9. Systeem berekent de volgende onderhoudsdatum.
10. Facility Manager ontvangt eventueel een notificatie.

## 11. Storings- en herstellingsbeheer

### 11.1 Storing melden

Een storing kan worden gemeld vanaf:

- QR-landingspagina;
- toestelpagina;
- siteoverzicht;
- mobiele interface;
- API;
- import.

De melder kan meegeven:

- omschrijving;
- foutcode;
- foto of video;
- urgentie;
- impact op werking;
- veiligheidsrisico;
- contactgegevens indien toegelaten.

### 11.2 Herstelling

Een herstelling wordt gekoppeld aan één of meer storingen.

De registratie bevat:

- diagnose;
- hoofdoorzaak;
- uitgevoerde handelingen;
- vervangen onderdelen;
- begin- en eindtijd;
- technieker;
- interne werkuren;
- externe kosten;
- totale kost;
- testresultaat;
- toestelstatus na interventie;
- aanbeveling;
- garantie op herstelling.

### 11.3 Herhalingsanalyse

Storingen worden geclassificeerd met gestandaardiseerde storings- en oorzaakcodes. Daardoor kan het systeem herkennen:

- dezelfde fout op hetzelfde toestel;
- hetzelfde probleem op hetzelfde model;
- dezelfde fout over meerdere sites;
- terugkerende storing binnen een configureerbare periode;
- abnormaal hoge storingsfrequentie.

## 12. Keuringsbeheer

Een toestel kan nul, één of meerdere keuringsschema's hebben.

Een keuringsschema bevat:

- keuringstype;
- wettelijke of interne basis;
- interval;
- bevoegde uitvoerders;
- vereiste documenten;
- herinneringstermijnen;
- escalatieregels;
- gevolgen bij vervallen of afgekeurde keuring.

Bij een afgekeurde keuring kan het systeem automatisch:

- toestelstatus op `afgekeurd` of `buiten dienst` zetten;
- een herstelactie aanmaken;
- verantwoordelijken informeren;
- gebruik blokkeren volgens organisatiebeleid.

## 13. Planning en meldingen

Het systeem ondersteunt geplande acties voor:

- preventief onderhoud;
- wettelijke keuring;
- kalibratie;
- garantie-einde;
- vervanging;
- inspectie;
- periodieke controle.

Mogelijke notificaties:

- onderhoud binnen 30 dagen;
- onderhoud vervallen;
- keuring binnen 60 dagen;
- keuring vervallen;
- kritieke storing gemeld;
- herstelling niet tijdig gestart;
- toestel herhaaldelijk defect;
- document of attest vervalt;
- garantie bijna verlopen.

Notificaties worden gekoppeld aan rollen, sites en organisaties.

## 14. Rapporten en statistieken

### 14.1 Toestelniveau

Voor één toestel worden minimaal getoond:

- aantal storingen per periode;
- aantal herstellingen;
- aantal onderhoudsbeurten;
- aantal keuringen;
- totale stilstand;
- gemiddelde hersteltijd;
- gemiddelde tijd tussen storingen;
- totale onderhouds- en herstellingskosten;
- meest voorkomende storingscodes;
- meest voorkomende oorzaken;
- compliancegraad van onderhoud en keuringen.

Voorbeeldvraag:

> Hoeveel keer is toestel X stuk gegaan in de laatste vijf jaar?

De telling is gebaseerd op geregistreerde storingsgebeurtenissen binnen de gekozen periode. De gebruiker kan kiezen of herhaalde meldingen binnen dezelfde interventie als één storing of als afzonderlijke meldingen worden geteld.

### 14.2 Organisatieniveau

Voor de organisatie worden onder meer berekend:

- totaal aantal actieve toestellen;
- toestellen per soort, merk, model en site;
- defectpercentage;
- aantal storingen per maand en jaar;
- storingsfrequentie per 100 toestellen;
- top 10 meest defecte toestellen;
- top 10 modellen met meeste storingen;
- gemiddelde hersteltijd;
- gemiddelde stilstand;
- totale kosten;
- kosten per toestelsoort;
- onderhoud op tijd uitgevoerd;
- vervallen onderhoudstaken;
- keuringen op tijd uitgevoerd;
- vervallen keuringen;
- afgekeurde toestellen;
- gemiddelde leeftijd van toestellen;
- vervangingsprognose;
- vergelijking tussen sites.

### 14.3 Statistische definities

Belangrijke indicatoren:

```text
Storingsfrequentie = aantal storingen / aantal actieve toestellen
```

```text
MTTR = totale hersteltijd / aantal afgesloten herstellingen
```

```text
MTBF = totale operationele tijd / aantal storingen
```

```text
Onderhoudscompliance = tijdig uitgevoerde onderhoudstaken / vervallen onderhoudstaken
```

De exacte definities, inclusiecriteria en tijdzones worden centraal vastgelegd zodat rapporten reproduceerbaar zijn.

### 14.4 Filters

Rapporten kunnen worden gefilterd op:

- organisatie;
- franchise;
- site;
- gebouw;
- ruimte;
- merk;
- model;
- soort;
- categorie;
- status;
- criticiteit;
- onderhoudspartner;
- datumperiode;
- leeftijd;
- garantie;
- storingscode;
- oorzaakcode.

### 14.5 Export

Ondersteunde exportformaten:

- CSV;
- XLSX;
- PDF;
- API-response.

Export respecteert dezelfde autorisatie en datascoping als de schermen.

## 15. Dashboard

### 15.1 Site Facility Manager dashboard

Toont onder meer:

- actieve toestellen op de site;
- defecte toestellen;
- kritieke open storingen;
- onderhoud vandaag en komende 30 dagen;
- vervallen onderhoud;
- keuringen komende 60 dagen;
- afgekeurde toestellen;
- gemiddelde hersteltijd;
- recente QR-meldingen;
- top terugkerende defecten.

### 15.2 Franchisee dashboard

Toont onder meer:

- vergelijking tussen sites;
- storingsfrequentie per site;
- onderhoudscompliance per site;
- keuringscompliance per site;
- kosten per site;
- modellen met structurele problemen;
- vervangingsbehoefte;
- trends over vijf jaar;
- benchmark ten opzichte van de organisatie.

## 16. Datamodel

### 16.1 Stamtabellen

#### `asset_brands`

- `id`
- `organization_id` nullable voor centrale catalogus
- `name`
- `normalized_name`
- `manufacturer_name`
- `is_active`
- `created_at`
- `updated_at`

#### `asset_types`

- `id`
- `organization_id` nullable
- `code`
- `name`
- `description`
- `parent_type_id` nullable
- `is_active`

#### `asset_categories`

- `id`
- `organization_id` nullable
- `code`
- `name`
- `parent_category_id` nullable
- `is_active`

#### `asset_models`

- `id`
- `brand_id`
- `asset_type_id`
- `model_name`
- `model_code`
- `technical_properties` JSONB
- `default_maintenance_interval_days` nullable
- `expected_lifetime_months` nullable
- `is_active`

### 16.2 Toestellen

#### `assets`

- `id` UUID
- `asset_code` uniek en onveranderlijk
- `organization_id`
- `site_id` nullable
- `building_id` nullable
- `floor_id` nullable
- `room_id` nullable
- `asset_type_id`
- `asset_category_id` nullable
- `brand_id` nullable
- `model_id` nullable
- `display_name`
- `serial_number` nullable
- `inventory_number` nullable
- `status`
- `criticality`
- `commissioned_at` nullable
- `purchase_date` nullable
- `warranty_until` nullable
- `purchase_cost` nullable
- `currency` nullable
- `supplier_id` nullable
- `responsible_user_id` nullable
- `responsible_team_id` nullable
- `technical_properties` JSONB
- `notes` nullable
- `main_document_id` nullable
- `created_by`
- `created_at`
- `updated_at`
- `archived_at` nullable

Belangrijke constraints:

- `asset_code` is uniek;
- organisatie is verplicht;
- verwijdering gebeurt logisch via archivering;
- organisatie van site en toestel moet overeenkomen;
- statuswaarden worden gevalideerd;
- auditvelden zijn verplicht.

### 16.3 Locatiehistorie

#### `asset_location_history`

- `id`
- `asset_id`
- `organization_id`
- `site_id`
- `building_id` nullable
- `floor_id` nullable
- `room_id` nullable
- `valid_from`
- `valid_until` nullable
- `reason`
- `changed_by`

### 16.4 QR-labels

#### `asset_qr_labels`

- `id`
- `asset_id`
- `token_hash`
- `token_prefix`
- `label_type`
- `status`
- `created_at`
- `created_by`
- `printed_at` nullable
- `last_scanned_at` nullable
- `scan_count`
- `revoked_at` nullable
- `revoked_by` nullable
- `revocation_reason` nullable

De ruwe QR-token wordt niet in logs opgeslagen. In de database wordt bij voorkeur alleen een hash bewaard, vergelijkbaar met een API-token.

### 16.5 Gebeurtenissen

#### `asset_events`

- `id`
- `asset_id`
- `organization_id`
- `event_type`
- `event_time`
- `status_before` nullable
- `status_after` nullable
- `title`
- `description` nullable
- `source`
- `actor_user_id` nullable
- `external_actor_name` nullable
- `related_entity_type` nullable
- `related_entity_id` nullable
- `metadata` JSONB
- `created_at`

### 16.6 Onderhoud

#### `maintenance_plans`

- `id`
- `organization_id`
- `asset_id` nullable
- `asset_type_id` nullable
- `model_id` nullable
- `maintenance_type_id`
- `interval_days` nullable
- `interval_months` nullable
- `usage_interval` nullable
- `is_mandatory`
- `is_active`
- `checklist_template_id` nullable

#### `maintenance_tasks`

- `id`
- `asset_id`
- `maintenance_plan_id` nullable
- `scheduled_for`
- `due_at` nullable
- `status`
- `assigned_user_id` nullable
- `assigned_supplier_id` nullable
- `started_at` nullable
- `completed_at` nullable
- `confirmed_at` nullable
- `confirmed_by` nullable
- `result`
- `notes` nullable
- `next_due_at` nullable
- `labor_minutes` nullable
- `material_cost` nullable
- `labor_cost` nullable
- `external_cost` nullable
- `total_cost` nullable
- `created_at`

### 16.7 Storingen en herstellingen

#### `asset_faults`

- `id`
- `asset_id`
- `fault_code_id` nullable
- `reported_at`
- `reported_by` nullable
- `source`
- `priority`
- `impact`
- `safety_risk`
- `description`
- `status`
- `first_response_at` nullable
- `resolved_at` nullable
- `downtime_minutes` nullable
- `parent_fault_id` nullable
- `created_at`

#### `asset_repairs`

- `id`
- `asset_id`
- `fault_id` nullable
- `started_at`
- `completed_at` nullable
- `technician_user_id` nullable
- `supplier_id` nullable
- `diagnosis`
- `root_cause_code_id` nullable
- `work_performed`
- `test_result` nullable
- `status_after`
- `labor_minutes` nullable
- `material_cost` nullable
- `labor_cost` nullable
- `external_cost` nullable
- `total_cost` nullable
- `warranty_until` nullable
- `created_at`

#### `repair_parts`

- `id`
- `repair_id`
- `part_code`
- `description`
- `quantity`
- `unit_cost` nullable
- `total_cost` nullable

### 16.8 Keuringen

#### `asset_inspection_plans`

- `id`
- `organization_id`
- `asset_id` nullable
- `asset_type_id` nullable
- `inspection_type_id`
- `interval_months`
- `warning_days`
- `is_mandatory`
- `is_active`

#### `asset_inspections`

- `id`
- `asset_id`
- `inspection_plan_id` nullable
- `inspection_date`
- `expires_at` nullable
- `inspector_user_id` nullable
- `inspection_company_id` nullable
- `result`
- `findings` nullable
- `corrective_action_required`
- `status_after` nullable
- `certificate_document_id` nullable
- `created_at`

### 16.9 Documentkoppeling

#### `asset_documents`

- `id`
- `asset_id`
- `document_id`
- `document_category`
- `is_primary`
- `valid_from` nullable
- `valid_until` nullable
- `created_by`
- `created_at`

Documentinhoud wordt niet dubbel opgeslagen. De bestaande documententabel en immutable opslag worden hergebruikt.

## 17. API-ontwerp

Basisroute:

```text
/api/v1/assets
```

### 17.1 Toestellen

```text
GET    /api/v1/assets
POST   /api/v1/assets
GET    /api/v1/assets/{asset_id}
PATCH  /api/v1/assets/{asset_id}
POST   /api/v1/assets/{asset_id}/archive
POST   /api/v1/assets/{asset_id}/move
GET    /api/v1/assets/{asset_id}/timeline
GET    /api/v1/assets/{asset_id}/statistics
```

### 17.2 QR-codes

```text
POST   /api/v1/assets/{asset_id}/qr-labels
GET    /api/v1/assets/{asset_id}/qr-labels
POST   /api/v1/assets/{asset_id}/qr-labels/{label_id}/revoke
GET    /q/{token}
```

`GET /q/{token}` is een resolver en geeft bij voorkeur een korte redirect naar de canonical toestelroute.

### 17.3 Onderhoud

```text
GET    /api/v1/assets/{asset_id}/maintenance
POST   /api/v1/assets/{asset_id}/maintenance
GET    /api/v1/maintenance-tasks/{task_id}
PATCH  /api/v1/maintenance-tasks/{task_id}
POST   /api/v1/maintenance-tasks/{task_id}/start
POST   /api/v1/maintenance-tasks/{task_id}/complete
POST   /api/v1/maintenance-tasks/{task_id}/confirm
```

### 17.4 Storingen

```text
GET    /api/v1/assets/{asset_id}/faults
POST   /api/v1/assets/{asset_id}/faults
GET    /api/v1/faults/{fault_id}
PATCH  /api/v1/faults/{fault_id}
POST   /api/v1/faults/{fault_id}/assign
POST   /api/v1/faults/{fault_id}/close
```

### 17.5 Herstellingen

```text
POST   /api/v1/assets/{asset_id}/repairs
GET    /api/v1/repairs/{repair_id}
PATCH  /api/v1/repairs/{repair_id}
POST   /api/v1/repairs/{repair_id}/complete
```

### 17.6 Keuringen

```text
GET    /api/v1/assets/{asset_id}/inspections
POST   /api/v1/assets/{asset_id}/inspections
GET    /api/v1/inspections/{inspection_id}
PATCH  /api/v1/inspections/{inspection_id}
```

### 17.7 Documenten

```text
GET    /api/v1/assets/{asset_id}/documents
POST   /api/v1/assets/{asset_id}/documents
DELETE /api/v1/assets/{asset_id}/documents/{link_id}
```

### 17.8 Rapporten

```text
GET /api/v1/reports/assets/overview
GET /api/v1/reports/assets/faults
GET /api/v1/reports/assets/maintenance-compliance
GET /api/v1/reports/assets/inspection-compliance
GET /api/v1/reports/assets/costs
GET /api/v1/reports/assets/reliability
GET /api/v1/reports/assets/site-comparison
POST /api/v1/reports/assets/export
```

## 18. Voorbeeld API-responses

### 18.1 Toestel

```json
{
  "id": "1e4b8f47-1b2e-4704-94c1-83ab3f1cb450",
  "asset_code": "AST_000001247",
  "display_name": "Koelcel keuken 1",
  "organization_id": "org_123",
  "site_id": "site_456",
  "type": {
    "code": "COOLING_UNIT",
    "name": "Koelinstallatie"
  },
  "brand": "ExampleBrand",
  "model": "CF-500",
  "serial_number": "SN-2024-00189",
  "status": "active",
  "criticality": "high",
  "next_maintenance_at": "2026-09-15",
  "next_inspection_at": "2027-01-10",
  "open_faults": 1
}
```

### 18.2 Statistieken over vijf jaar

```json
{
  "asset_id": "1e4b8f47-1b2e-4704-94c1-83ab3f1cb450",
  "period": {
    "from": "2021-01-01",
    "to": "2025-12-31"
  },
  "fault_count": 12,
  "repair_count": 10,
  "total_downtime_minutes": 8460,
  "mttr_minutes": 846,
  "mtbf_hours": 3120,
  "maintenance_cost": 4200.50,
  "repair_cost": 7850.00,
  "most_common_fault_codes": [
    {
      "code": "TEMP_HIGH",
      "count": 5
    }
  ]
}
```

## 19. UI/UX

### 19.1 Toestellenoverzicht

Kolommen:

- statusindicator;
- toestelnummer;
- naam;
- site;
- locatie;
- soort;
- merk;
- model;
- open storingen;
- volgend onderhoud;
- volgende keuring;
- criticiteit;
- acties.

Beschikbare weergaven:

- tabel;
- kaarten;
- per site;
- per ruimte;
- per toestelsoort;
- defecte toestellen;
- onderhoudskalender;
- keuringskalender.

### 19.2 Mobiele QR-pagina

De QR-pagina is mobile-first.

Bovenaan staan:

- duidelijke toestelnaam;
- statuskleur en tekst;
- locatie;
- hoofdafbeelding;
- toestelnummer;
- grote actieknoppen.

Actieknoppen:

- storing melden;
- onderhoud bevestigen;
- herstelling registreren;
- keuring toevoegen;
- foto toevoegen;
- handleiding openen;
- volledige historie bekijken.

### 19.3 Toestel aanmaken

Wizardstappen:

1. Organisatie en site.
2. Soort en categorie.
3. Merk en model.
4. Identificatie en serienummer.
5. Locatie.
6. Onderhoud en keuringen.
7. Documenten en foto's.
8. QR-code genereren.
9. Controle en opslaan.

### 19.4 QR-label afdrukken

De gebruiker kan kiezen uit vooraf ingestelde formaten.

Het label bevat minimaal:

- QR-code;
- toestelnummer;
- korte toestelnaam;
- optioneel sitenaam;
- tekst zoals `Scan voor toestelinfo`.

De URL of token wordt niet als enige leesbare identificatie gebruikt. Het toestelnummer blijft zichtbaar voor manuele ondersteuning.

## 20. Zoeken

Toestellen zijn doorzoekbaar op:

- toestelnummer;
- inventarisnummer;
- serienummer;
- naam;
- merk;
- model;
- soort;
- categorie;
- site;
- ruimte;
- storingscode;
- documenttekst via OCR;
- vrije tekst uit onderhouds- en herstellingsnotities, binnen autorisatiegrenzen.

## 21. AI- en RAG-integratie

Gekoppelde handleidingen, plannen, onderhoudsrapporten en keuringsattesten kunnen in de bestaande RAG-laag worden opgenomen.

Mogelijke vragen:

- Welke onderhoudsinstructie geldt voor dit toestel?
- Welke onderdelen zijn nodig voor foutcode E17?
- Welke terugkerende problemen zijn bekend voor dit model?
- Vat de herstellingen van de laatste vijf jaar samen.
- Vergelijk de storingsfrequentie van dit model met andere modellen.
- Welke keuringen verlopen binnen zestig dagen?

AI-antwoorden moeten:

- de autorisatie van de gebruiker respecteren;
- bronnen tonen;
- geen acties automatisch bevestigen;
- geen wettelijke of veiligheidsbeslissing autonoom nemen;
- duidelijk onderscheid maken tussen geregistreerde feiten en AI-inferentie.

## 22. Audit en compliance

Audit-events worden minimaal geregistreerd voor:

- toestel aangemaakt;
- toestel gewijzigd;
- toestel verplaatst;
- status gewijzigd;
- QR-label aangemaakt;
- QR-label ingetrokken;
- onderhoud gestart of bevestigd;
- storing gemeld;
- herstelling afgesloten;
- keuring geregistreerd;
- document gekoppeld of verwijderd;
- rapport geëxporteerd;
- gevoelige toestelgegevens geraadpleegd waar vereist.

Historische onderhouds-, storings-, herstellings- en keuringsregistraties worden niet fysiek verwijderd via de normale gebruikersinterface. Correcties gebeuren via versie, annulering of tegenboeking met reden.

## 23. Autorisatie en datascoping

Elke query wordt gescopeerd op:

- organisatie;
- toegewezen sites;
- rol;
- expliciete rechten;
- eventueel externe onderhoudsopdracht.

Een gebruiker mag een QR-token kunnen oplossen zonder daarmee automatisch alle toestelgegevens te mogen bekijken.

De backend bepaalt welke velden en acties zichtbaar zijn. De frontend is nooit de enige autorisatielaag.

## 24. Securitymaatregelen

- QR-tokens zijn onvoorspelbaar en intrekbaar.
- Tokens worden niet als plain text gelogd.
- Rate limiting op QR-resolver en publieke meldflow.
- Uploads worden gecontroleerd op bestandstype, grootte en malware.
- Documenttoegang gebruikt gesigneerde of geautoriseerde downloads.
- Kritieke wijzigingen vereisen step-up authenticatie wanneer organisatiebeleid dit voorschrijft.
- Externe techniekerstoegang is tijdsgebonden en opdrachtgebonden.
- Alle mutaties worden server-side gevalideerd.
- Organisatie- en sitegrenzen worden in elke query afgedwongen.

## 25. Performance en aggregaties

Voor organisatierapporten worden waar nodig vooraf berekende aggregaties of materialized views gebruikt.

Aanbevolen aggregaties:

- storingen per toestel per maand;
- kosten per toestel per maand;
- stilstand per toestel per maand;
- onderhoudscompliance per site per maand;
- keuringscompliance per site per maand;
- MTTR en MTBF per toestel en model;
- actieve toestellen per categorie en site.

Rapportages over vijf of meer jaar mogen de transactietabellen niet onnodig zwaar belasten.

## 26. Indexen

Minimaal aanbevolen database-indexen:

- `assets(organization_id, site_id, status)`;
- `assets(asset_code)` uniek;
- `assets(serial_number)` waar niet leeg;
- `assets(asset_type_id, brand_id, model_id)`;
- `asset_events(asset_id, event_time desc)`;
- `asset_faults(asset_id, reported_at desc)`;
- `asset_faults(organization_id, status, reported_at)` via denormalisatie of joinstrategie;
- `asset_repairs(asset_id, completed_at desc)`;
- `maintenance_tasks(asset_id, scheduled_for)`;
- `maintenance_tasks(status, due_at)`;
- `asset_inspections(asset_id, inspection_date desc)`;
- `asset_inspections(expires_at, result)`;
- `asset_qr_labels(token_hash)` uniek;
- `asset_documents(asset_id, document_category)`.

## 27. Import en migratie

Bestaande toestellijsten kunnen via CSV of XLSX worden geïmporteerd.

Importstappen:

1. Bestand uploaden.
2. Kolommen mappen.
3. Merken, modellen, soorten en sites normaliseren.
4. Duplicaten detecteren.
5. Validaties uitvoeren.
6. Simulatierapport tonen.
7. Import bevestigen.
8. Toestelnummers genereren.
9. Optioneel QR-labels in batch genereren.
10. Auditrapport bewaren.

Duplicaatdetectie gebruikt onder meer:

- serienummer;
- inventarisnummer;
- combinatie merk, model en locatie;
- bestaand extern referentienummer.

## 28. Batchfuncties

Bevoegde gebruikers kunnen:

- meerdere toestellen verplaatsen;
- categorie of verantwoordelijke wijzigen;
- onderhoudsplannen toewijzen;
- keuringsschema's toewijzen;
- QR-labels genereren;
- labels als PDF exporteren;
- toestellen archiveren;
- rapporten exporteren.

Elke batchactie toont vooraf het aantal getroffen toestellen en vereist bevestiging.

## 29. Acceptatiecriteria

De module is functioneel aanvaard wanneer minimaal:

1. Een organisatiebeheerder merken, soorten en categorieën kan beheren.
2. Een Facility Manager een toestel kan aanmaken.
3. Een toestel een onveranderlijk toestelnummer krijgt.
4. Een QR-label kan worden gegenereerd en afgedrukt.
5. Een QR-scan naar de correcte toestelpagina leidt.
6. Onbevoegde gebruikers geen gevoelige toestelgegevens zien.
7. Een onderhoud via de toestelpagina kan worden bevestigd.
8. Een storing kan worden gemeld.
9. Een herstelling aan een storing kan worden gekoppeld.
10. Een keuring en keuringsattest kunnen worden geregistreerd.
11. Foto's, handleidingen en plannen kunnen worden gekoppeld.
12. De volledige historie chronologisch zichtbaar is.
13. Een Facility Manager sitegebonden overzichten kan bekijken.
14. Een franchisee organisatiewijde statistieken kan bekijken.
15. De vraag `hoeveel keer is toestel X stuk gegaan in de laatste vijf jaar` reproduceerbaar kan worden beantwoord.
16. Organisatiestatistieken filterbaar en exporteerbaar zijn.
17. QR-tokens kunnen worden ingetrokken en vervangen.
18. Alle mutaties auditbaar zijn.

## 30. Teststrategie

### Functionele tests

- toestel aanmaken en wijzigen;
- classificatie;
- locatieverplaatsing;
- QR genereren, scannen, intrekken en vervangen;
- onderhoud bevestigen;
- storing melden;
- herstelling registreren;
- keuring registreren;
- document koppelen;
- statistieken over vijf jaar;
- organisatie- en sitefilters.

### Autorisatietests

- Facility Manager ziet alleen toegewezen sites;
- franchisee ziet toegestane organisatiegegevens;
- externe technieker ziet alleen toegewezen opdrachten;
- publieke QR-gebruiker ziet alleen beperkte gegevens;
- documentdownloads respecteren rollen;
- exports respecteren datascoping.

### Securitytests

- QR-token enumeration;
- rate limiting;
- ingetrokken token;
- verlopen externe toegang;
- uploadvalidatie;
- cross-organization access;
- manipulatie van asset-id en site-id;
- auditlogcontrole.

### Performancetests

- organisatie met honderdduizenden toestellen;
- vijf tot tien jaar gebeurtenishistorie;
- QR-scan tijdens piekbelasting;
- dashboardaggregaties;
- grote exports;
- gelijktijdige documentuploads.

## 31. Gefaseerde implementatie

### Fase 1 — Basisregister

- toestelclassificatie;
- toestelregistratie;
- site- en locatiekoppeling;
- foto's en documenten;
- QR-code;
- toestelpagina;
- audit.

### Fase 2 — Operationele opvolging

- onderhoud;
- storingen;
- herstellingen;
- keuringen;
- notificaties;
- mobiele QR-flow.

### Fase 3 — Rapportering

- toestelstatistieken;
- organisatie- en sitedashboards;
- kostenanalyse;
- MTTR en MTBF;
- exports;
- trendanalyse over vijf jaar.

### Fase 4 — Geavanceerde functies

- AI-samenvattingen;
- RAG over handleidingen en historie;
- voorspellend onderhoud;
- automatische anomaliedetectie;
- koppelingen met leveranciers en IoT;
- automatische tellerstanden.

## 32. Architectuurbeslissingen

1. **Toestel is een afzonderlijk domeinobject.**  
   Een toestel is geen document en wordt niet uitsluitend als metadata van een keuring opgeslagen.

2. **Documentbeheer wordt hergebruikt.**  
   Handleidingen, foto's, plannen, attesten en werkbonnen blijven documenten in de bestaande documentmodule en worden via relaties aan toestellen gekoppeld.

3. **QR-code is een resolver, geen autorisatiebewijs.**  
   Het bezit van de QR-code geeft niet automatisch toegang tot gevoelige informatie of mutaties.

4. **Toestelnummer is onveranderlijk.**  
   Locatie, naam, merkclassificatie of organisatorische metadata mogen wijzigen zonder dat het toestelnummer verandert.

5. **Gebeurtenissen zijn historisch en auditbaar.**  
   Onderhoud, storingen, herstellingen en keuringen worden als afzonderlijke transacties opgeslagen en niet als één overschrijfbaar tekstveld.

6. **Statistieken zijn reproduceerbaar.**  
   Definities van storing, stilstand, MTTR, MTBF en compliance worden centraal vastgelegd.

7. **Organisatiescheiding wordt backendmatig afgedwongen.**  
   De QR-landingspagina en rapportage vormen geen uitzondering op tenant- en site-isolatie.

8. **Mobile-first voor QR-gebruik.**  
   De toestelpagina wordt ontworpen voor gebruik op smartphone door Facility Managers en techniekers.

9. **Nginx en Django zijn niet vereist voor deze module.**  
   De module wordt geïmplementeerd binnen de bestaande React- en FastAPI-architectuur.