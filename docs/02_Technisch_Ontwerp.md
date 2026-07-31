# Technisch Ontwerp

## Digitaal Keurings- en Documentbeheer

**Versie:** 0.5 Concept  
**Status:** Eerste voorontwerp, aangevuld na review

## 1. Doel van dit document

Dit document beschrijft de voorgestelde technische architectuur voor het platform voor digitaal keurings- en documentbeheer. Het vormt de technische vertaling van het functioneel ontwerp en dient als basis voor ontwikkeling, installatie, beveiliging, testen en beheer.

## 2. Architectuurprincipes

Het systeem wordt modulair opgebouwd. Elke module heeft een duidelijk afgebakende verantwoordelijkheid en communiceert via goed gedefinieerde interfaces.

Belangrijke principes:

- Webgebaseerde applicatie
- Scheiding tussen frontend, backend, database, opslag en AI-verwerking
- Centrale registratie van metadata in PostgreSQL
- Bestandsopslag op een configureerbare Synology NAS
- Asynchrone verwerking van zware taken
- Volledige logging en audittrail
- AI-resultaten worden eerst gevalideerd voordat ze definitief worden opgeslagen
- Beheerinstellingen zijn via de webinterface configureerbaar
- Uitrol via Docker Compose op Debian 12 VM's binnen Proxmox
- Sterke authenticatie op basis van TOTP en WebAuthn/Passkeys
- Biometrische verificatie blijft bij het besturingssysteem of de authenticator; de applicatie bewaart geen biometrische gegevens

## 3. Systeemoverzicht

```text
Browser
  |
  v
Webfrontend
  |
  v
REST API / Backend
  |
  +--> Sterke authenticatie, WebAuthn/TOTP en autorisatie
  +--> Organisatie- en sitebeheer
  +--> Documentbeheer
  +--> Keuringsbeheer
  +--> Risicoanalyse
  +--> Rapportering
  +--> Beheer en configuratie
  |
  +--> Job Queue --> Worker Services
  |                  +--> OCR
  |                  +--> AI-analyse
  |                  +--> Bestandsverwerking
  |                  +--> E-mailverwerking
  |
  +--> PostgreSQL
  +--> Synology NAS
  +--> Lokale AI-server
```

## 4. Voorgestelde technische componenten

### 4.1 Frontend

Voorgestelde technologie:

- React
- TypeScript
- Responsive webinterface
- REST API als communicatielaag
- Browser WebAuthn API voor Passkeys en FIDO2-security keys

Belangrijkste verantwoordelijkheden:

- Aanmelding met wachtwoord, TOTP of Passkey volgens het geldende beleid
- Registratie en beheer van Passkeys
- Starten en afhandelen van WebAuthn-challenges
- Step-up authenticatie voor gevoelige acties
- Dashboards
- Documentupload via drag-and-drop
- Controle en correctie van AI-resultaten
- Site- en organisatiebeheer
- Gebruikers- en rechtenbeheer
- Beheer van systeeminstellingen

### 4.2 Backend

Voorgestelde technologie:

- Python
- FastAPI
- Gunicorn met geschikte workerconfiguratie
- SQLAlchemy voor database-interactie
- Alembic voor databasemigraties
- WebAuthn/FIDO2-bibliotheek met verificatie van registraties en assertions

Belangrijkste verantwoordelijkheden:

- REST API
- Bedrijfslogica
- Authenticatie, WebAuthn, TOTP en autorisatie
- Uitgifte, opslag en eenmalige validatie van challenges
- Verificatie van origin, RP ID, signatures en sign counters
- Validatie
- Documentregistratie
- Aansturen van achtergrondtaken
- Integraties met opslag, AI en e-mail

### 4.3 Database

Voorgestelde technologie:

- PostgreSQL

De database bevat alle structurele gegevens en metadata. Bestanden zelf worden niet als primaire opslag in PostgreSQL bewaard.

Voor sterke authenticatie bevat PostgreSQL uitsluitend de noodzakelijke technische gegevens, zoals publieke WebAuthn-credentials, gehashte herstelcodes, TOTP-configuratie en auditinformatie. Biometrische gegevens worden nooit in de applicatiedatabase opgeslagen.

### 4.4 Bestandsopslag

Voorgestelde opslag:

- Synology NAS
- Configureerbare netwerkshare
- Opslag per organisatie en site

De database blijft de bron van waarheid. De mappenstructuur op de NAS dient uitsluitend voor fysieke bestandsopslag.

De fysieke sitemap wordt gebaseerd op een onveranderlijke interne opslagcode en niet op de zichtbare sitenaam of het functionele sitenummer. Hierdoor hoeft de fysieke hoofdmap niet te worden hernoemd wanneer:

- een tijdelijke Site een definitief sitenummer krijgt;
- de sitenaam wordt gecorrigeerd of gewijzigd;
- de schrijfwijze van een Site verandert;
- een Site administratief wordt hernummerd.

Voorbeeld:

```text
Zichtbare tijdelijke Site: Putte_TMP001
Zichtbare definitieve Site: Putte_185
Fysieke opslagmap: SITE_00001247
```

De opslagcode is uniek, onveranderlijk en gekoppeld aan de permanente `site_id`.

### 4.5 Achtergrondtaken

Voor langdurige of zware processen wordt een job queue gebruikt.

Voorbeelden:

- OCR
- AI-analyse
- PDF-verwerking
- Historische migratie
- E-mailinname
- Reminderverwerking
- PostgreSQL-back-uptaken

Voorgestelde componenten:

- Redis
- Celery of RQ
- Afzonderlijke workercontainers

## 5. AI-architectuur

De AI-laag wordt losgekoppeld van de kernapplicatie.

### 5.1 AI Job Flow

```text
Document upload
  -> AI-job aanmaken
  -> OCR of Vision selecteren
  -> Model selecteren op basis van jobtype
  -> Prompt uitvoeren
  -> Response ontvangen
  -> JSON valideren
  -> Resultaat opslaan als voorstel
  -> Gebruiker controleert en bevestigt
```

### 5.2 Ondersteuning van meerdere modellen

Per AI-model worden minimaal volgende instellingen beheerd:

- Naam
- Type
- Serveradres
- Modelidentifier
- Ondersteunde jobtypes
- Timeout
- Maximale retries
- Actief/inactief

### 5.3 AI-diagnose

Per AI-job worden minimaal bewaard:

- Start- en eindtijd
- Duur
- Gebruikt model
- Gebruikte prompt
- Ruwe response
- Gevalideerd resultaat
- Foutmeldingen
- Aantal retries
- Gebruiker die de job startte

## 6. Documentverwerking

### 6.1 Upload

- Ondersteuning voor meerdere bestanden
- Maximale bestandsgrootte: 100 MB per bestand
- Toegestane bestandstypes: PDF, JPG/JPEG, DWG en XLSX
- Controle op bestandsextensie en MIME-type
- Berekening van een bestandshash
- Detectie van mogelijke duplicaten
- Tijdelijke quarantaine-opslag tijdens verwerking

Bestanden die groter zijn dan 100 MB of een niet-ondersteund bestandstype hebben, worden geweigerd met een duidelijke foutmelding.

### 6.2 Definitieve opslag

Een document wordt pas definitief opgeslagen nadat:

- het bestand technisch gevalideerd is;
- de metadata beschikbaar is;
- de sitekoppeling bevestigd is;
- de voorgestelde bestandsnaam gevalideerd is.

### 6.3 Bestandsnaamconventie

De bestandsnaamconventie in dit hoofdstuk is de enige technische bron van waarheid voor het volledige project. Alle modules die bestanden aanmaken, importeren, exporteren, verplaatsen of hernoemen moeten deze conventie gebruiken.

Voorgesteld formaat:

```text
Site_Sitenummer_Disciplinecode_Documenttypecode_DatumTijd.ext
```

Voorbeeld:

```text
Aalst_36_HOO_FOT_20260606133325.jpg
```

De exacte codes en naamgevingsregels worden centraal beheerd in de database.

#### 6.3.1 Centrale Naamgevingsservice

Alle bestandsnamen worden uitsluitend gegenereerd en gevalideerd door een centrale Naamgevingsservice. Geen frontendmodule, backendmodule, achtergrondworker, AI-component of importproces mag zelfstandig een definitieve bestandsnaam samenstellen.

De Naamgevingsservice is verantwoordelijk voor:

- samenstellen van de bestandsnaam volgens de geldende conventie;
- valideren van verplichte naamcomponenten en hun volgorde;
- normaliseren van toegestane tekens en scheidingstekens;
- behouden van de correcte bestandsextensie;
- controleren van de maximale bestandsnaamlengte;
- detecteren van naamconflicten;
- genereren van een volgnummer wanneer dit noodzakelijk is;
- bepalen van de onveranderlijke fysieke opslagmap;
- voorbereiden en uitvoeren van gecontroleerde hernoem- en verplaatsoperaties.

Een bestandsnaam is afgeleid van metadata en vormt nooit de primaire identiteit van een document. Relaties verwijzen naar onveranderlijke identifiers, zoals `document_id`, `document_version_id` en `site_id`.

#### 6.3.2 Eén-voor-één-generatie

Bestandsnamen worden altijd één voor één gegenereerd en gevalideerd, ook bij een batchupload of een migratie van een volledige Site.

De verwerking per bestand verloopt in deze volgorde:

1. Lees de actuele metadata uit de database.
2. Genereer één voorgestelde bestandsnaam.
3. Valideer de naam tegen de centrale conventie.
4. Controleer onmiddellijk of de naam en het doelpad uniek zijn.
5. Reserveer de naam voor de lopende operatie.
6. Hernoem of verplaats uitsluitend dit ene bestand.
7. Controleer of het bestand op de nieuwe locatie bestaat en de hash ongewijzigd is.
8. Werk de database en auditregistratie voor dit bestand bij.
9. Markeer het bestand als voltooid.
10. Start pas daarna de verwerking van het volgende bestand.

Parallel genereren of parallel hernoemen van bestandsnamen binnen dezelfde Site is niet toegestaan. Hiermee worden dubbele volgnummers, race conditions, onjuiste doelpaden en gedeeltelijk overschreven bestanden vermeden.

Een batchjob mag meerdere bestanden bevatten, maar de daadwerkelijke naamgeneratie en bestandsmutatie worden sequentieel uitgevoerd.

#### 6.3.3 Naamconflicten en volgnummers

Bij een naamconflict controleert het systeem eerst of het bestand:

- een duplicaat is;
- een nieuwe versie van een bestaand document is;
- of een werkelijk nieuw bestand is.

Een nieuwe documentversie wordt gekoppeld aan het bestaande document en krijgt geen willekeurige afwijkende naam.

Voor een werkelijk nieuw bestand mag de Naamgevingsservice uitsluitend een volgnummer toevoegen als laatste onderdeel vóór de extensie. De overige onderdelen van de conventie mogen niet worden gewijzigd, verwijderd of herschikt.

Voorbeeld:

```text
Aalst_36_HOO_FOT_20260606133325.jpg
Aalst_36_HOO_FOT_20260606133325_01.jpg
Aalst_36_HOO_FOT_20260606133325_02.jpg
```

Ook het bepalen van een volgnummer gebeurt één voor één. Het nummer wordt pas definitief toegekend nadat de naam succesvol is gereserveerd.

Handmatig hernoemen is alleen toegestaan via de Naamgevingsservice en moet volledig voldoen aan de geldende conventie.

#### 6.3.4 Tijdelijke sitenummers

Een Site in aanbouw kan reeds bekend zijn terwijl nog geen definitief sitenummer is toegekend. In dat geval kent het systeem een uniek tijdelijk sitenummer toe met formaat:

```text
TMPnnn
```

Voorbeeld van de zichtbare site-identificatie:

```text
Putte_TMP001
```

De tijdelijke site-identificatie wordt gebruikt in:

- de bestandsnamen;
- de gebruikersinterface;
- exports en rapportverwijzingen waarin de Site-identificatie wordt opgenomen.

Voorbeeld:

```text
Zichtbare Site:
Putte_TMP001

Bestandsnaam:
Putte_TMP001_HOO_FOT_20260606133325.jpg

Fysieke opslagmap:
SITE_00001247
```

De tijdelijke code moet uniek zijn binnen de organisatie. De permanente `site_id` en fysieke opslagcode blijven tijdens en na de tijdelijke fase ongewijzigd.

#### 6.3.5 Onveranderlijke fysieke sitemap

Elke Site krijgt bij creatie één unieke fysieke opslagcode. Deze code wordt slechts eenmaal gegenereerd en wordt daarna nooit aangepast.

Aanbevolen formaat:

```text
SITE_nnnnnnnn
```

Voorbeeld:

```text
SITE_00001247
```

De zichtbare sitenaam en het functionele sitenummer maken geen deel uit van de fysieke hoofdmapnaam.

De koppeling wordt in PostgreSQL opgeslagen:

```text
site_id                 = 7e3d...
site_name               = Putte
site_number             = TMP001
storage_code            = SITE_00001247
storage_relative_path   = SITE_00001247
```

Na toekenning van het definitieve sitenummer verandert uitsluitend de functionele metadata:

```text
site_name               = Putte
site_number             = 185
storage_code            = SITE_00001247
storage_relative_path   = SITE_00001247
```

De fysieke hoofdmap blijft dus bestaan als:

```text
SITE_00001247
```

Hierdoor ontstaat geen risicovolle mapmigratie bij een wijziging van de sitenaam of het sitenummer.

#### 6.3.6 Toekenning van een definitief sitenummer

Wanneer een tijdelijke Site een definitief sitenummer krijgt, start een bevoegde gebruiker een gecontroleerde bestandsnaammigratie.

Voorbeeld:

```text
Oude zichtbare Site: Putte_TMP001
Nieuwe zichtbare Site: Putte_185
Fysieke opslagmap: SITE_00001247 (ongewijzigd)
```

Alle betrokken bestandsnamen worden één voor één opnieuw gegenereerd volgens dezelfde centrale bestandsnaamconventie.

Voorbeeld:

```text
Oude bestandsnaam:
Putte_TMP001_HOO_FOT_20260606133325.jpg

Nieuwe bestandsnaam:
Putte_185_HOO_FOT_20260606133325.jpg
```

De migratie omvat minimaal:

- validatie van het nieuwe definitieve sitenummer;
- bevestiging dat de permanente `site_id` en `storage_code` ongewijzigd blijven;
- één-voor-één genereren van alle nieuwe bestandsnamen;
- één-voor-één hernoemen van de bestanden binnen dezelfde fysieke sitemap;
- verificatie van bestandshash en doelpad na ieder bestand;
- bijwerken van databasevelden en interne verwijzingen na ieder bestand;
- bijwerken van zoek- en AI-metadata zonder onnodige herberekening van documentinhoud;
- volledige auditregistratie en een eindrapport.

De fysieke hoofdmap wordt niet hernoemd. Alleen de bestanden en functionele metadata worden aangepast.

Aangezien er geen automatische SharePoint-integratie bestaat, wordt uitsluitend de interne SharePoint-statusmarkering behouden. Eventuele externe SharePoint-bestanden moeten buiten het systeem handmatig worden hernoemd of verplaatst.

#### 6.3.7 Volgorde van de sitemigratie

De migratie verloopt gecontroleerd en sequentieel:

```text
Voorcontrole
  -> Simulatie en migratieplan
  -> Definitief sitenummer registreren als geplande wijziging
  -> Bestand 1 genereren, valideren, hernoemen en registreren
  -> Bestand 2 genereren, valideren, hernoemen en registreren
  -> ...
  -> Laatste bestand controleren
  -> Site-metadata definitief activeren
  -> Eindcontrole
  -> Migratierapport
```

Het systeem start de verwerking van een volgend bestand pas wanneer het vorige bestand volledig is afgerond.

De wijziging van het functionele sitenummer wordt pas definitief geactiveerd nadat:

- alle doelbestandsnamen zijn gevalideerd;
- alle bestanden succesvol zijn hernoemd;
- alle bestandshashes zijn gecontroleerd;
- alle databaseverwijzingen correct zijn bijgewerkt;
- geen onopgeloste naamconflicten bestaan.

De fysieke opslagmap en `storage_code` blijven gedurende het volledige proces ongewijzigd.

#### 6.3.8 Hervatten en herstel

De sitemigratie is een achtergrondjob met een duurzame voortgangsregistratie. Per bestand wordt bewaard:

- oude bestandsnaam en oud pad;
- nieuwe bestandsnaam en nieuw pad;
- oorspronkelijke bestandshash;
- migratiestatus;
- foutmelding;
- start- en eindtijd;
- gebruiker die de migratie heeft gestart.

Bij een fout stopt de migratie vóór het volgende bestand. De beheerder kan de fout herstellen en de job vanaf het eerstvolgende niet-voltooide bestand hervatten.

Een reeds succesvol verwerkt bestand wordt niet opnieuw hernoemd. Een rollback gebruikt dezelfde één-voor-één-procedure in omgekeerde richting.

Omdat de fysieke hoofdmap onveranderd blijft, beperkt een rollback zich tot bestandsnamen en functionele Site-metadata.

#### 6.3.9 Simulatie en goedkeuring

Voor de definitieve migratie is een simulatie verplicht. Deze toont minimaal:

- oude en nieuwe zichtbare Site-identificatie;
- ongewijzigde fysieke opslagcode;
- aantal betrokken bestanden;
- oude en nieuwe bestandsnaam per bestand;
- gevonden duplicaten en conflicten;
- ontbrekende bestanden;
- geschatte verwerkingstijd;
- vereiste handmatige acties.

De definitieve migratie kan alleen worden gestart wanneer alle blokkerende fouten zijn opgelost en een bevoegde gebruiker het migratieplan expliciet bevestigt.

#### 6.3.10 Audit

Iedere naamgeneratie, hernoeming en sitemigratie is auditplichtig.

De auditregistratie bevat minimaal:

- actor;
- datum en tijd;
- reden of jobtype;
- oude en nieuwe zichtbare Site-identificatie;
- onveranderlijke fysieke opslagcode;
- oude en nieuwe bestandsnaam;
- document- en versie-ID;
- resultaat;
- eventuele foutmelding.

## 7. Beveiliging

### 7.1 Basismatregelen

Minimale maatregelen:

- Versleutelde verbinding via HTTPS
- Sterke wachtwoordhashing
- Sessiebeheer met veilige, kortlevende tokens
- Sterke authenticatie via TOTP en WebAuthn/Passkeys
- Role Based Access Control
- Autorisatie op organisatieniveau en siteniveau
- Auditlogging
- Bescherming tegen ongeoorloofde bestandstoegang
- Validatie van uploads
- Geheimen niet opslaan in broncode
- Rate limiting en tijdelijke blokkering bij herhaalde mislukte aanmeldingen
- Bescherming tegen CSRF, XSS, replay-aanvallen en sessiefixatie

Voor administrators is sterke authenticatie verplicht. Voor andere gebruikers is de verplichting configureerbaar per organisatie en rol. SMS- en e-mailcodes worden niet als sterke authenticatiemethode ondersteund.

### 7.2 TOTP

TOTP blijft beschikbaar als ondersteunde methode en als terugvaloptie wanneer dit volgens het organisatiebeleid is toegestaan.

De implementatie omvat:

- compatibiliteit met gangbare authenticator-apps;
- registratie via een eenmalige QR-code en handmatige sleutel;
- versleutelde opslag van het TOTP-geheim;
- tolerantie voor een beperkte klokafwijking;
- bescherming tegen hergebruik van dezelfde code binnen het geldigheidsvenster;
- gecontroleerde herregistratie na recente step-up authenticatie;
- eenmalige herstelcodes die uitsluitend gehasht worden opgeslagen.

### 7.3 WebAuthn en Passkeys

WebAuthn/FIDO2 is de voorkeursmethode voor sterke authenticatie. De browser communiceert met een platformauthenticator of roaming authenticator, zoals:

- Windows Hello;
- Touch ID of Face ID;
- Android-biometrie of apparaat-PIN;
- ingebouwde vingerafdruk- of gezichtsherkenning;
- hardware security keys.

De biometrische controle gebeurt volledig lokaal door het apparaat of de authenticator. De applicatie ontvangt en bewaart geen biometrische kenmerken, foto's, gezichtssjablonen of vingerafdrukken.

Per WebAuthn-credential bewaart de backend minimaal:

- credential ID;
- publieke sleutel;
- gebruiker en tenant/organisatie;
- sign counter, indien door de authenticator ondersteund;
- transports;
- authenticator attachment, indien beschikbaar;
- discoverable/resident-key-eigenschap;
- door de gebruiker gekozen apparaatnaam;
- creatie-, laatste-gebruik- en intrekkingsdatum.

Private sleutels verlaten de authenticator nooit.

### 7.4 Relying Party en originvalidatie

De WebAuthn-configuratie gebruikt een expliciet ingestelde Relying Party ID en een beperkte lijst toegestane HTTPS-origins. De backend valideert bij elke registratie en aanmelding:

- challenge;
- origin;
- RP ID hash;
- type van de client data;
- cryptografische signature;
- user presence;
- user verification volgens het ingestelde beleid;
- credentialstatus en intrekkingsstatus;
- sign counter wanneer bruikbaar.

Challenges zijn cryptografisch willekeurig, kort geldig, aan één sessie en beoogde actie gekoppeld en slechts eenmaal bruikbaar. Redis kan worden gebruikt voor tijdelijke challengeopslag; beveiligingsrelevante resultaten en credentials worden duurzaam in PostgreSQL bewaard.

### 7.5 Registratie en aanmelding

Registratie van een Passkey vereist een recent geauthenticeerde sessie en step-up verificatie. De backend maakt registratieopties aan, waarna de browser de authenticator aanspreekt en de backend de attestation en clientdata valideert.

De aanmeldflow ondersteunt:

- gebruikersnaam of e-mailadres gevolgd door een gerichte WebAuthn-challenge;
- usernameless login met discoverable credentials, wanneer geactiveerd;
- wachtwoord plus TOTP;
- wachtwoord plus Passkey;
- volledig wachtwoordloze Passkey-login, wanneer door het beleid toegestaan.

Na succesvolle verificatie geeft de backend pas een applicatiesessie of JWT-tokens uit. De sessie registreert de gebruikte authenticatiemethode en het tijdstip waarop sterke authenticatie of step-up verificatie plaatsvond.

### 7.6 Step-up authenticatie

Voor gevoelige acties is een recente aanvullende verificatie vereist. Voorbeelden:

- toevoegen of verwijderen van authenticatiemethoden;
- genereren van herstelcodes;
- aanpassen van rollen of beveiligingsbeleid;
- uitvoeren van administratieve exports;
- starten, hervatten of terugdraaien van een sitemigratie;
- intrekken van sessies van andere gebruikers.

Step-up gebeurt bij voorkeur met een Passkey en kan, wanneer toegestaan, met TOTP. De geldigheidsduur van een step-up bevestiging is kort en configureerbaar.

### 7.7 Herstel, intrekking en apparaatbeheer

Gebruikers kunnen meerdere Passkeys registreren en een herkenbare apparaatnaam toekennen. Een credential kan onmiddellijk worden ingetrokken. Het verwijderen van de laatste bruikbare methode wordt geblokkeerd, tenzij een bevoegde administrator een gecontroleerde herstelprocedure uitvoert.

Herstel verloopt in deze volgorde:

1. een andere geregistreerde Passkey;
2. TOTP;
3. een eenmalige herstelcode;
4. een administratieve herstelprocedure met identiteitscontrole.

Na gebruik van een herstelcode wordt deze onmiddellijk ongeldig. Het genereren van een nieuwe set maakt de vorige set volledig ongeldig. Beveiligingswijzigingen leiden tot een auditrecord en kunnen bestaande sessies intrekken.

### 7.8 Sessies en tokens

JWT-toegangstokens zijn kort geldig. Refresh tokens worden veilig opgeslagen, geroteerd en kunnen per sessie of apparaat worden ingetrokken. Cookies gebruiken minimaal `Secure`, `HttpOnly` en een passende `SameSite`-instelling.

De backend bewaart voldoende sessiemetadata om actieve sessies te tonen en gericht in te trekken. Een wijziging van wachtwoord, intrekking van een authenticatiemethode of administratieve blokkering kan alle bestaande sessies ongeldig maken.

## 8. Logging en monitoring

Het systeem onderscheidt:

- Applicatielogs
- Auditlogs
- AI-logs
- Joblogs
- Integratielogs
- Securitylogs

Logs moeten via de beheerinterface gedeeltelijk raadpleegbaar zijn. Gevoelige informatie, waaronder TOTP-geheimen, WebAuthn-challenges, herstelcodes, wachtwoorden, private sleutels en tokens, wordt nooit in logs opgenomen.

Securitylogs bevatten minimaal geslaagde en mislukte aanmeldingen, registratie en intrekking van authenticatiemethoden, herstelacties, step-up verificaties, sessie-intrekkingen en beleidswijzigingen. Publieke credential-ID's worden alleen gelogd wanneer dit noodzakelijk is en dan bij voorkeur gepseudonimiseerd.

## 9. Deployment

Voorgestelde VM-verdeling binnen Proxmox:

### VM 1 - Webapplicatie

- Debian 12
- Docker Compose
- Frontend
- Backend
- Reverse proxy

### VM 2 - Database

- Debian 12
- PostgreSQL
- Geautomatiseerde back-ups naar de Synology NAS

### VM 3 - AI-server

- Lokale modellen
- Vision- en tekstmodellen
- Configureerbare API

### Externe opslag

- Synology NAS
- Documentopslag
- PostgreSQL-back-upopslag

## 10. Back-up en herstel

Minimale back-upstrategie:

- Dagelijkse geautomatiseerde PostgreSQL-back-up naar een afzonderlijke back-upmap op de Synology NAS
- Extra PostgreSQL-back-up vóór iedere applicatie- of database-update
- Datum- en tijdsaanduiding in iedere back-upbestandsnaam
- Controle en logging van het resultaat van iedere back-uptaak
- Configureerbaar retentiebeleid voor dagelijkse, wekelijkse en maandelijkse back-ups
- De back-upmap wordt logisch gescheiden van de gewone documentopslag
- Versiebeheer van configuratie
- NAS-back-up volgens bedrijfsbeleid
- Periodieke test van de herstelprocedure
- Gedocumenteerde herstelprocedure
- Mogelijkheid tot rollback bij een mislukte update

Een update mag niet starten wanneer de verplichte voorafgaande PostgreSQL-back-up mislukt.

## 11. Integraties en externe koppelingen

Voorziene koppelingen:

- Synology NAS
- E-mailinbox keuringen@elecon.be
- SMTP voor reminders
- Excel import en export
- Lokale AI-server

### 11.1 SharePoint-markering

Er wordt geen technische SharePoint-integratie gebouwd.

Op organisatieniveau kan de SharePoint-functionaliteit met een eenvoudige instelling worden geactiveerd of gedeactiveerd. Wanneer deze instelling actief is, kan een bevoegd gebruiker per document aanduiden of het document naar SharePoint werd geüpload.

Bij deze markering worden minimaal bewaard:

- SharePoint-status: aangevinkt of niet aangevinkt
- Datum en tijd van markering
- Gebruiker die de status wijzigde

Het systeem verstuurt of synchroniseert zelf geen bestanden naar SharePoint.

## 12. Bevestigde en openstaande ontwerpbeslissingen

### Bevestigd

- Sterke authenticatie ondersteunt TOTP en WebAuthn/Passkeys
- WebAuthn/Passkeys is de voorkeursmethode en TOTP blijft beschikbaar als fallback volgens beleid
- Biometrische gegevens worden niet door de applicatie opgeslagen; verificatie gebeurt lokaal door het besturingssysteem of de authenticator
- Administrators moeten sterke authenticatie gebruiken
- Wachtwoordloze Passkey-login en usernameless login zijn configureerbaar
- SMS- en e-mailcodes worden niet als sterke authenticatiemethode ondersteund
- PostgreSQL-back-ups worden op de Synology NAS opgeslagen
- Geen technische SharePoint-integratie; uitsluitend een handmatige statusmarkering
- Maximale bestandsgrootte: 100 MB per bestand
- Ondersteunde bestandstypes: PDF, JPG/JPEG, DWG en XLSX
- De bestandsnaamconventie wordt projectbreed afgedwongen door één centrale Naamgevingsservice
- Bestandsnamen en bestandsmutaties worden altijd één voor één verwerkt
- Tijdelijke Sites gebruiken een unieke `TMPnnn`-code
- Elke Site krijgt een unieke, onveranderlijke fysieke opslagcode
- De fysieke hoofdmap bevat geen zichtbare sitenaam of functioneel sitenummer
- Bij toekenning van een definitief sitenummer worden de betrokken bestanden gecontroleerd hernoemd, maar blijft de fysieke sitemap ongewijzigd

### Nog te bevestigen

- Definitieve frontendtechnologie
- Celery of RQ
- Het exacte organisatiebeleid voor verplichte authenticatiemethoden bij niet-administrators
- Exacte toegestane WebAuthn-origins en definitieve RP ID per omgeving
- Attestationbeleid voor hardware security keys
- Netwerkprotocol voor NAS-toegang
- Retentiebeleid voor logs
- Exacte retentie van PostgreSQL-back-ups
- Strategie voor hoge beschikbaarheid

## 13. Volgende uitwerking

In de volgende versie worden toegevoegd:

- Componentdiagram
- Deploymentdiagram
- Netwerkdiagram
- API-conventies
- Verdere detaillering van het beveiligingsmodel
- Foutafhandeling
- Monitoringstrategie
- Teststrategie
- Installatie- en updateprocedure