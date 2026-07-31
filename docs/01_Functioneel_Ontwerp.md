# Functioneel Ontwerp

## Digitaal Keurings- en Documentbeheer

**Versie:** 0.4 Concept

## Inleiding

Het doel van dit project is het ontwikkelen van een centraal webgebaseerd platform voor het beheren van technische documenten, keuringsverslagen en risicoanalyses. De applicatie automatiseert documentverwerking met behulp van AI en biedt een centrale omgeving voor organisaties, sites en gebruikers.

## Doelstellingen

- Centraliseren van alle technische documenten
- Automatisch classificeren van documenten
- Opvolgen van wettelijke keuringen en vervaldata
- AI-ondersteunde documentanalyse
- Ondersteuning van meerdere organisaties
- Integratie met de Synology NAS
- Handmatige SharePoint-status per document
- Registreren van menselijke correcties om de documentherkenning stapsgewijs te verbeteren
- Veilige toegang via sterke authenticatie met TOTP en WebAuthn/Passkeys

## Hoofdmodules

- Organisatiebeheer
- Gebruikersbeheer
- Sitebeheer
- Documentbeheer
- AI-verwerking
- Keuringsbeheer
- Risicoanalyse
- Dashboard
- Keuringsplanning
- Historische migratie
- Rapportering
- Beheer

## Gebruikersrollen

### Administrator
Volledige systeemrechten.

### Gebruiker
Uploaden en beheren van documenten binnen toegewezen organisaties.

### Site Facility Manager
Beheer van één of meerdere sites.

### Site Manager
Leesrechten en uploadrechten voor toegewezen sites.

## Sterke authenticatie

### Ondersteunde methoden

Het platform ondersteunt sterke authenticatie via meerdere methoden:

- Wachtwoord in combinatie met een TOTP-code uit een authenticator-app
- Wachtwoord in combinatie met een Passkey via WebAuthn/FIDO2
- Wachtwoordloze aanmelding via een Passkey, wanneer dit door een administrator is geactiveerd
- Hardware security keys die WebAuthn/FIDO2 ondersteunen
- Eenmalige herstelcodes als gecontroleerde noodprocedure

Passkeys kunnen door het apparaat of besturingssysteem worden ontgrendeld met onder meer:

- Windows Hello
- Gezichtsherkenning
- Vingerafdruk
- PIN
- Touch ID
- Face ID
- Android-biometrie

De applicatie slaat zelf geen gezichtssjablonen, vingerafdrukken of andere biometrische gegevens op. De lokale authenticator of het besturingssysteem voert de biometrische verificatie uit. Het platform bewaart uitsluitend de publieke WebAuthn-credentialgegevens die nodig zijn om de aanmelding cryptografisch te controleren.

### Verplichting en beleid

Voor administrators is sterke authenticatie verplicht. Per organisatie kan worden ingesteld welke sterke authenticatiemethoden voor andere gebruikers verplicht, toegestaan of uitgeschakeld zijn. SMS-codes en e-mailcodes gelden niet als ondersteunde sterke authenticatiemethode.

Een gebruiker moet minimaal één actieve sterke authenticatiemethode hebben voordat toegang tot beveiligde functionaliteit wordt toegestaan. Organisatiebeleid kan vereisen dat een gebruiker twee herstelbare methoden registreert, bijvoorbeeld een Passkey en TOTP.

### Beheer door de gebruiker

Een gebruiker kan binnen het eigen profiel:

- meerdere Passkeys registreren;
- een herkenbare apparaatnaam aan een Passkey toekennen;
- de laatst gebruikte datum bekijken;
- een Passkey intrekken;
- TOTP activeren of opnieuw registreren;
- nieuwe herstelcodes genereren, waarbij bestaande herstelcodes ongeldig worden;
- een standaard aanmeldmethode kiezen, voor zover het organisatiebeleid dit toestaat.

Het verwijderen van de laatste bruikbare sterke authenticatiemethode is niet toegestaan zonder dat eerst een vervangende methode is geregistreerd of een administrator een gecontroleerde herstelprocedure uitvoert.

### Step-up authenticatie

Voor kritieke handelingen kan het systeem een recente aanvullende bevestiging vragen, ook wanneer de gebruiker reeds is aangemeld. Dit geldt minimaal voor:

- wijzigen van authenticatiemethoden;
- genereren van nieuwe herstelcodes;
- beheren van gebruikers en rollen;
- aanpassen van beveiligingsinstellingen;
- starten of terugdraaien van een sitemigratie;
- uitvoeren van andere door een administrator als gevoelig gemarkeerde acties.

De bevestiging gebeurt bij voorkeur met een Passkey en kan, wanneer toegestaan, met een geldige TOTP-code plaatsvinden.

### Herstel en verlies van een toestel

Wanneer een gebruiker geen toegang meer heeft tot een geregistreerd toestel, kan deze:

1. een andere reeds geregistreerde Passkey gebruiken;
2. TOTP gebruiken;
3. een geldige eenmalige herstelcode gebruiken;
4. een gecontroleerde herstelprocedure via een bevoegde administrator starten.

Elke herstelactie, registratie, intrekking en mislukte verificatie wordt in de security- en auditlog opgenomen.

## Sites

Een Site is de centrale entiteit binnen het systeem. Alle documenten, risicoanalyses, keuringen en foto's worden gekoppeld aan een Site.

## Documentverwerking

1. Upload document
2. Bestand valideren
3. OCR indien nodig
4. AI-analyse uitvoeren
5. Metadata herkennen
6. Voorstel tonen
7. Gebruiker controleert verplichte velden
8. Menselijke correcties registreren
9. Definitieve opslag

AI doet voorstellen, maar de gebruiker behoudt steeds de eindcontrole alvorens gegevens definitief worden opgeslagen.

## Keuringsdocumenten

### Herkende gegevens

Bij het inlezen van een keuringsdocument probeert het systeem minimaal volgende gegevens te herkennen:

- Site
- Discipline
- Datum van onderzoek
- Datum van verslag
- Keuringsstatus
- Eventuele opmerkingen

### Datumprioriteit

Voor het bepalen van de keuringsdatum geldt volgende prioriteit:

1. Datum van onderzoek
2. Datum van verslag
3. Creatiedatum van het PDF-bestand, uitsluitend wanneer geen bruikbare datum in het document werd gevonden
4. Manuele invoer

De datum van onderzoek is dus altijd primair ten opzichte van de datum van het verslag.

### Keuringsstatus

Elke keuring moet manueel gecontroleerd en bevestigd worden. De keuzelijst bevat:

- `-------------`
- Goedgekeurd
- Goedgekeurd met opmerkingen
- Afgekeurd

De waarde `-------------` is de standaardwaarde en stelt voor dat nog geen geldige status bevestigd is.

Wanneer de status niet betrouwbaar door AI kan worden herkend, blijft de keuzelijst op `-------------` staan. De gebruiker moet dan verplicht een geldige status selecteren. Een keuringsdocument kan niet definitief worden opgeslagen zolang de standaardwaarde geselecteerd blijft.

Ook wanneer AI een status voorstelt, moet de gebruiker deze controleren en bevestigen.

### Vervaltermijn per discipline

Iedere discipline kan een configureerbare vervaltermijn krijgen. Deze termijn wordt beheerd door een administrator en moet later uitbreidbaar en wijzigbaar zijn.

Voorbeelden:

- Hoogspanning: 1 jaar
- Laagspanning: 5 jaar

De termijn wordt niet hard in de programmacode vastgelegd, maar via beheerinstellingen opgeslagen.

### Automatisch berekende vervaldatum

Wanneer de datum van onderzoek wordt herkend of manueel ingevoerd, berekent het systeem automatisch een voorgestelde vervaldatum:

```text
vervaldatum = datum van onderzoek + vervaltermijn van de discipline
```

Wanneer geen datum van onderzoek beschikbaar is, wordt de datum van verslag gebruikt. Wanneer ook die ontbreekt, kan de creatiedatum van de PDF als voorstel worden gebruikt.

De voorgestelde vervaldatum moet zichtbaar en manueel aanpasbaar zijn vóór definitieve opslag.

Wanneer voor een discipline nog geen vervaltermijn is ingesteld, wordt geen vervaldatum automatisch berekend en moet de gebruiker deze manueel invullen of de disciplineconfiguratie aanvullen.

## Fotoverwerking

### Batchupload

Foto's mogen in batch worden opgeladen naar een vooraf geselecteerde Site.

Wanneer de Site vooraf door de gebruiker is gekozen, mogen foto's zonder afzonderlijke bevestiging per bestand rechtstreeks bij die Site worden geplaatst, op voorwaarde dat er geen afwijking wordt vastgesteld.

Voor iedere foto wordt vóór definitieve opslag automatisch een nieuwe bestandsnaam samengesteld volgens de centrale bestandsnaamconventie. De oorspronkelijke bestandsnaam blijft als metadata bewaard voor traceerbaarheid.

Voorgesteld formaat:

```text
Site_Sitenummer_Disciplinecode_Documenttypecode_DatumTijd.ext
```

Voorbeeld:

```text
Aalst_36_ALG_FOT_20260730194523.jpg
```

Wanneer de discipline bij de batchupload niet van toepassing of niet gekend is, wordt een configureerbare algemene disciplinecode gebruikt. De definitieve codes worden centraal beheerd.

Bij een naamconflict wordt een uniek volgnummer of unieke suffix toegevoegd. Bestaande bestanden worden nooit stilzwijgend overschreven.

### Fotodatum

Het systeem probeert de datum van de foto in volgende volgorde te bepalen:

1. Datum uit de oorspronkelijke bestandsnaam
2. Beschikbare metadata van het afbeeldingsbestand
3. Bestandscreatiedatum
4. Manuele invoer

Wanneer de gevonden datum geldig en logisch is, wordt de foto automatisch verwerkt en wordt deze datum gebruikt in de nieuwe bestandsnaam. Bij ontbrekende, ongeldige of afwijkende datums wordt de foto gemarkeerd voor manuele controle.

Voorbeelden van afwijkingen:

- Datum kan niet worden herkend
- Datum ligt onwaarschijnlijk ver in het verleden of de toekomst
- Bestandsnaam en metadata bevatten tegenstrijdige datums
- Meerdere datumformaten leveren geen eenduidig resultaat

## PDF-datumherkenning

Voor PDF-documenten probeert het systeem eerst datums uit de zichtbare documentinhoud te herkennen.

De volgorde is:

1. Datum van onderzoek
2. Datum van verslag
3. Andere duidelijk benoemde relevante documentdatum
4. PDF-creatiedatum uit de bestandsmetadata
5. Manuele invoer

De PDF-creatiedatum mag alleen als terugvalwaarde worden gebruikt wanneer geen relevante datum uit de documentinhoud werd gevonden. De bron van de gekozen datum wordt steeds opgeslagen, zodat later zichtbaar blijft of de datum uit het document, uit metadata of uit manuele invoer kwam.

## Leren uit menselijke correcties

### Feedbackregistratie

Wanneer een gebruiker een AI-voorstel aanpast, bewaart het systeem zowel het oorspronkelijke voorstel als de definitief bevestigde waarde.

Per correctie worden minimaal geregistreerd:

- Document en documenttype
- Gebruikt AI-model en modelversie
- Gebruikte promptversie
- Door AI voorgestelde waarde
- Door gebruiker bevestigde waarde
- Gecorrigeerd veld, bijvoorbeeld Site, discipline, datum of status
- Betrouwbaarheidsscore van het AI-voorstel, indien beschikbaar
- Gebruiker en tijdstip van correctie

### Wijze van verbeteren

Het systeem wijzigt het AI-model niet onmiddellijk na iedere afzonderlijke correctie. Direct automatisch doorleren kan ongewenste fouten versterken en maakt de werking moeilijk controleerbaar.

De correcties worden gebruikt voor een gecontroleerde verbetercyclus:

1. Correcties verzamelen
2. Terugkerende foutpatronen analyseren
3. Herkenningsregels en prompts verbeteren
4. Nieuwe configuratie testen op een vaste testset
5. Resultaten vergelijken met de vorige versie
6. Verbetering na goedkeuring activeren

Op korte termijn leert het systeem dus vooral via verbeterde regels, voorbeelden en prompts. Op langere termijn kunnen voldoende gecontroleerde correcties als trainings- of evaluatiedataset worden gebruikt voor een gespecialiseerd model of fine-tuning.

### Automatische patroonregels

Voor veel voorkomende en eenduidige correcties kan een administrator een herkenningsregel goedkeuren. Voorbeelden:

- Een vaste benaming op documenten koppelen aan een bekende Site
- Een afkorting koppelen aan een discipline
- Een terugkerende formulering koppelen aan een keuringsstatus

Nieuwe regels worden eerst getest en mogen bestaande documenten niet met terugwerkende kracht aanpassen zonder expliciete goedkeuring.

### Kwaliteitsbewaking

Het beheerscherm toont minimaal:

- Aantal geanalyseerde documenten
- Percentage ongewijzigd bevestigde voorstellen
- Correctiepercentage per veld
- Correctiepercentage per documenttype
- Correctiepercentage per AI-model en promptversie
- Meest voorkomende fouten

Hiermee kan objectief worden vastgesteld of een nieuwe prompt, regel of modelversie daadwerkelijk beter presteert.

## Validatieregels

Een keuringsdocument kan pas definitief worden opgeslagen wanneer minimaal volgende gegevens geldig zijn:

- Site
- Discipline
- Keuringsstatus verschillend van `-------------`
- Keuringsdatum
- Vervaldatum, indien voor de discipline een vervaltermijn geldt

Het systeem registreert wie de gegevens heeft gecontroleerd en wanneer de controle werd uitgevoerd.

---

Dit document is een concept en zal tijdens de analysefase verder worden uitgebreid met alle functionele specificaties, schermbeschrijvingen en procesflows.
