# UI/UX Ontwerp

## Digitaal Keurings- en Documentbeheer

**Versie:** 1.1 Concept  
**Status:** Ontwerpvoorstel

## 1. Doel

Dit document beschrijft de gebruikersinterface en gebruikerservaring van het Digitaal Keurings- en Documentbeheer. Het vertaalt het functioneel en technisch ontwerp naar concrete schermen, interacties, statussen, validaties en gebruikersstromen.

De interface moet eenvoudig, snel en duidelijk zijn voor dagelijkse gebruikers, terwijl beheerders en validators voldoende detail en controle behouden.

## 2. Ontwerpprincipes

- Overwegend witte interface met accenten in de kleuren van de bedrijfsbranding.
- Duidelijke primaire en secundaire knoppen.
- Zo weinig mogelijk handmatige invoer wanneer gegevens afgeleid kunnen worden.
- Altijd zichtbare status bij AI- en achtergrondverwerking.
- Geen stille of schijnbaar vastgelopen schermen.
- Consistente navigatie, terminologie en validatiemeldingen.
- Responsive ontwerp voor desktop, laptop, tablet en mobiel.
- Toegankelijkheid volgens gangbare WCAG-principes.
- Meertaligheid vanaf de basisarchitectuur.
- Alle bestandsnamen worden uitsluitend via de centrale Naamgevingsservice afgehandeld zoals beschreven in `02_Technisch_Ontwerp.md`, hoofdstuk 6.3.
- Authenticatieschermen gebruiken de term **Sterke authenticatie** en niet uitsluitend **2FA**.
- Biometrische gegevens worden nooit door de applicatie opgevraagd, weergegeven of opgeslagen; de authenticator handelt biometrische verificatie lokaal af.

## 3. Visuele stijl

### 3.1 Branding

De interface gebruikt:

- wit als dominante achtergrond;
- bedrijfskleuren voor primaire acties, selecties en accenten;
- neutrale grijstinten voor secundaire informatie;
- groen voor geslaagde acties;
- oranje voor waarschuwingen;
- rood voor blokkerende fouten;
- blauw of de primaire bedrijfskleur voor actieve AI-processen.

### 3.2 Componenten

Belangrijkste componenten:

- zijmenu of compacte hoofdnavigatie;
- paginatitel met broodkruimelpad;
- overzichtskaarten;
- tabellen met sorteren, filteren en paginering;
- modale bevestigingen;
- statusbadges;
- voortgangsbalken;
- inline validatie;
- meldingen en notificatiecentrum;
- contextuele helpteksten.

## 4. Hoofdnavigatie

Voorgestelde hoofdnavigatie:

- Dashboard
- Sites
- Installaties
- Documenten
- Keuringen
- Bevindingen
- AI-validatie
- Kennis en zoeken
- Rapporten
- Notificaties
- Beheer

De zichtbare menu-items worden bepaald door de rol en het organisatie- en Sitebereik van de gebruiker.

## 5. Aanmelden en sterke authenticatie

### 5.1 Ondersteunde aanmeldmethoden

De interface ondersteunt, afhankelijk van het organisatiebeleid:

- wachtwoord met TOTP-code;
- wachtwoord met Passkey;
- wachtwoordloze Passkey-aanmelding;
- usernameless Passkey-aanmelding;
- FIDO2-security key;
- eenmalige herstelcode.

Passkeys kunnen lokaal worden ontgrendeld via onder meer:

- Windows Hello;
- Face ID;
- Touch ID;
- Android-biometrie;
- vingerafdruk of gezichtsherkenning van het toestel;
- toestel-PIN;
- hardware security key.

De applicatie voert zelf geen gezichts- of vingerafdrukherkenning uit en bewaart geen biometrische gegevens.

### 5.2 Aanmeldscherm

Het aanmeldscherm bevat:

- logo en applicatienaam;
- veld voor e-mailadres of gebruikersnaam;
- veld voor wachtwoord wanneer wachtwoordlogin wordt gebruikt;
- primaire knop **Aanmelden**;
- prominente knop **Aanmelden met passkey**;
- taalkeuze;
- link **Problemen met aanmelden?**;
- duidelijke foutmelding zonder gevoelige details prijs te geven.

Wanneer usernameless login is toegestaan, kan **Aanmelden met passkey** worden gekozen zonder vooraf een e-mailadres in te voeren.

De interface toont nooit of een specifiek e-mailadres wel of niet bestaat.

### 5.3 Keuze van sterke authenticatiemethode

Wanneer meerdere methoden geregistreerd zijn, toont het scherm:

- Passkey op dit apparaat;
- Passkey op een ander apparaat;
- Security key;
- Authenticator-app;
- Herstelcode.

De laatst gebruikte of door de gebruiker ingestelde voorkeursmethode mag als standaard worden voorgesteld. De gebruiker kan steeds **Andere methode gebruiken** kiezen.

### 5.4 Passkey-login

De Passkey-flow toont korte, apparaatneutrale instructies:

1. gebruiker kiest **Aanmelden met passkey**;
2. browser of besturingssysteem opent de authenticator;
3. gebruiker bevestigt lokaal met biometrie, PIN of security key;
4. de interface toont **Aanmelding controleren**;
5. na succesvolle verificatie wordt de gebruiker doorgestuurd.

De interface probeert geen eigen biometrische instructies na te bootsen. Teksten zoals **Bevestig op uw apparaat** hebben de voorkeur boven **Scan uw vingerafdruk**, omdat het gebruikte mechanisme per toestel verschilt.

Bij annulering toont het scherm geen foutstatus maar de neutrale melding **Aanmelding geannuleerd** en de mogelijkheid opnieuw te proberen of een andere methode te kiezen.

### 5.5 TOTP-login

Het TOTP-scherm bevat:

- zes invoervakken of één toegankelijk numeriek invoerveld;
- automatische focus en plakken van de volledige code;
- melding dat de code uit de authenticator-app komt;
- knop **Controleren**;
- link **Andere methode gebruiken**;
- geen countdown die onnodige druk veroorzaakt, tenzij duidelijk en toegankelijk weergegeven.

Na een fout wordt het veld leeggemaakt en blijft de focus correct staan. De melding maakt geen onderscheid tussen onbekende gebruiker, verkeerd wachtwoord of verkeerde tweede factor.

### 5.6 Eerste registratie van sterke authenticatie

Wanneer sterke authenticatie verplicht is en nog geen methode is geregistreerd, verschijnt een begeleide wizard:

1. uitleg waarom sterke authenticatie nodig is;
2. aanbevolen keuze **Passkey instellen**;
3. alternatief **Authenticator-app instellen**;
4. registratie en verificatie;
5. herstelcodes veilig tonen en laten bevestigen;
6. aanbeveling om een tweede herstelbare methode toe te voegen.

De wizard kan niet worden overgeslagen wanneer het beleid registratie verplicht.

### 5.7 Passkey registreren

Het registratiescherm bevat:

- korte uitleg dat de private sleutel op het apparaat blijft;
- veld **Naam van apparaat of sleutel**;
- knop **Passkey toevoegen**;
- ondersteuning voor platformauthenticator en security key;
- bevestigingsscherm met apparaatnaam en registratiedatum.

Voorbeelden van voorgestelde apparaatnamen:

- Laptop kantoor
- iPhone werk
- Android telefoon
- YubiKey sleutelbos

De gebruiker kan de naam voor of na registratie aanpassen.

### 5.8 TOTP instellen

Het TOTP-scherm toont:

- QR-code;
- handmatige instelsleutel als toegankelijk alternatief;
- verificatieveld voor de eerste code;
- waarschuwing dat de QR-code niet mag worden gedeeld;
- bevestiging zodra de methode actief is.

Na bevestiging wordt het TOTP-geheim niet opnieuw getoond.

### 5.9 Herstelcodes

Herstelcodes worden slechts eenmaal volledig getoond. Het scherm bevat:

- duidelijke waarschuwing om de codes veilig te bewaren;
- knop **Kopiëren**;
- knop **Afdrukken** waar dit beleidstechnisch is toegestaan;
- knop **Downloaden als tekstbestand** alleen wanneer dit veilig wordt geacht;
- bevestigingsvak **Ik heb mijn herstelcodes veilig bewaard**.

Het genereren van nieuwe codes maakt oude codes ongeldig en vereist step-up authenticatie.

## 6. Dashboard

Het dashboard bevat minimaal:

- keuringen die binnenkort vervallen;
- vervallen keuringen;
- openstaande AI-validaties;
- openstaande bulksteekproeven;
- recente uploads;
- mislukte achtergrondtaken;
- recente notificaties;
- snelle acties;
- AI-vraagveld.

### 6.1 AI-vraagveld

Op de hoofdpagina staat een duidelijk zichtbaar AI-vraagveld met:

- tekstinvoer;
- knop om de vraag te versturen;
- microfoonknop voor gesproken invoer;
- voorbeeldvragen;
- status van de verwerking;
- antwoord met bronverwijzingen;
- mogelijkheid om relevante documenten te openen.

### 6.2 Gesproken vragen

Bij gebruik van de microfoon:

1. vraagt de browser toestemming voor microfoongebruik;
2. toont de interface dat opname actief is;
3. kan de gebruiker de opname stoppen of annuleren;
4. wordt de spraak omgezet naar tekst;
5. krijgt de gebruiker de transcriptie te zien vóór of tijdens verzending;
6. kan de tekst handmatig worden gecorrigeerd.

## 7. Zichtbare feedback bij verwerking

Wanneer AI of een achtergrondtaak bezig is, toont de interface altijd zichtbare feedback.

Mogelijke statussen:

- Bestand ontvangen;
- Technische controle uitvoeren;
- OCR uitvoeren;
- AI-analyse uitvoeren;
- Metadata controleren;
- Bestandsnaam genereren;
- Bestand opslaan;
- Bronnen zoeken;
- Antwoord opstellen;
- Opnieuw proberen;
- Voltooid;
- Mislukt.

Langdurige processen tonen een spinner of voortgangsbalk, huidige stap, aantallen, starttijd, detailmogelijkheid en duidelijke foutmelding.

## 8. Meertaligheid

De applicatie is volledig lokalisatieklaar. De gebruiker kan de taal wijzigen via het aanmeldscherm, gebruikersmenu en persoonlijke voorkeuren.

Meertalig te beheren zijn menu's, labels, knoppen, validatie- en foutmeldingen, notificaties, e-mails, rapporttitels, AI-statusmeldingen, hulpteksten en referentiegegevens.

## 9. Uploadscherm

Het uploadscherm ondersteunt drag-and-drop, bestandsselectie, meerdere bestanden, duidelijke limieten, technische validatie, voortgang per bestand en totaaloverzicht.

Per bestand toont de interface onder meer oorspronkelijke bestandsnaam, type, grootte, duplicaatstatus, Site, discipline, documenttype, datum, voorgestelde definitieve bestandsnaam, AI-confidence, validatiefouten en verwerkingsstatus.

## 10. Bestandsnamen

### 10.1 Centrale regel

De UI stelt nooit zelfstandig een definitieve bestandsnaam samen. Alle voorstellen en validaties komen van de centrale Naamgevingsservice uit `02_Technisch_Ontwerp.md`, hoofdstuk 6.3.

### 10.2 Eén-voor-één-generatie

Ook bij batchuploads worden definitieve bestandsnamen één voor één gegenereerd en gereserveerd. De interface toont bijvoorbeeld:

```text
Bestand 12 van 84
Bestandsnaam controleren en reserveren...
```

### 10.3 Bestandsnaamconflicten

Bij een conflict krijgt de gebruiker een keuze op basis van het conflicttype: nieuwe versie, duplicaat overslaan, toegestaan volgnummer, metadata corrigeren of annuleren. Vrije hernoeming buiten de conventie is niet toegestaan.

## 11. AI-validatie

### 11.1 Individuele validatie

Het validatiescherm toont documentvoorbeeld, AI-gegevens, confidence, bestaande gegevens, correctievelden, waarschuwingen, bronpagina of beeldzone en acties voor bevestigen, corrigeren, afkeuren en later behandelen.

### 11.2 Snelle toetsenbordbediening

Voor frequente validators worden sneltoetsen voorzien voor bevestigen, navigeren, markeren en openen van het origineel.

### 11.3 AI-feedback

Iedere correctie wordt als feedback geregistreerd. Het oorspronkelijke voorstel blijft bewaard en de menselijke correctie vormt de definitieve waarde.

### 11.4 Bulkbevestigingen

Er zijn afzonderlijke tabbladen voor individuele validaties, bulkbevestigingen en steekproeven. Een afgekeurde steekproef kan de volledige batch opnieuw ter controle aanbieden.

## 12. Sitebeheer

Het Site-overzicht bevat zichtbare sitenaam, tijdelijk of definitief nummer, status, organisatie, aantallen en laatste activiteit.

### 12.1 Tijdelijke Sites

Een Site zonder definitief nummer krijgt een badge **Tijdelijk nummer** en voor bevoegde gebruikers de actie **Definitief sitenummer toekennen**.

### 12.2 Migratiewizard

De wizard toont huidige en nieuwe Site-identificatie, onveranderlijke opslagcode, aantal bestanden, simulatie, conflicten, duur, voortgang en eindrapport. Het starten, hervatten of terugdraaien van de migratie kan step-up authenticatie vereisen.

## 13. Documentoverzicht

Het documentoverzicht ondersteunt zoeken, sorteren, filters, opgeslagen filtersets, kolomkeuze, bulkselectie, export en documentdetails.

## 14. Documentdetail

Het documentdetail bevat tabbladen voor overzicht, bestand, versies, keuring, bevindingen, AI-analyse, relaties, audit en SharePoint-status.

## 15. Zoek- en kennisinterface

De kennisinterface bevat natuurlijke-taalvragen, klassieke zoeking, filters, resultaten, bronverwijzingen, documentfragmenten en feedback. De interface onderscheidt databasegegevens, documenttekst, AI-samenvatting en onzekerheden.

## 16. Rapporten

Grote rapporten worden als achtergrondjob uitgevoerd. De gebruiker kan verder werken en ontvangt na voltooiing een beveiligde download. Gevoelige exports kunnen step-up authenticatie vereisen.

## 17. Notificaties

Het notificatiecentrum toont bedrijfs- en beveiligingsmeldingen, waaronder:

- keuringen en validaties;
- mislukte imports, migraties en back-ups;
- voltooide rapporten;
- nieuwe of ingetrokken authenticatiemethoden;
- intrekking van sessies;
- gebruik van een herstelcode;
- accountblokkering of verdachte aanmeldpogingen.

## 18. Beheer van authenticatiemethoden en apparaten

### 18.1 Pagina **Beveiliging en aanmelden**

Deze pagina is bereikbaar via het gebruikersprofiel en toont:

- status van sterke authenticatie;
- voorkeursmethode;
- geregistreerde Passkeys;
- status van authenticator-app;
- aantal resterende herstelcodes;
- actieve sessies;
- recente beveiligingsactiviteit.

### 18.2 Passkeylijst

Per Passkey worden getoond:

- door de gebruiker gekozen naam;
- type: ingebouwd apparaat of security key;
- registratiedatum;
- laatst gebruikt;
- status;
- acties **Naam wijzigen** en **Verwijderen**.

Technische gegevens zoals publieke sleutels, credential-ID's en AAGUID's worden niet aan gewone gebruikers getoond.

### 18.3 Passkey verwijderen

Voor verwijderen verschijnt een bevestigingsdialoog met:

- naam van het apparaat;
- datum van laatste gebruik;
- waarschuwing dat aanmelden met deze Passkey daarna niet meer mogelijk is;
- step-up authenticatie;
- primaire knop **Passkey verwijderen**.

Bij de laatste bruikbare methode wordt verwijderen geblokkeerd met:

```text
Deze methode kan niet worden verwijderd.
Voeg eerst een andere passkey of authenticator-app toe.
```

### 18.4 Voorkeursmethode

De gebruiker kan een voorkeursmethode kiezen voor zover het organisatiebeleid dit toestaat. Dit bepaalt alleen welke methode eerst wordt voorgesteld en schakelt andere geregistreerde methoden niet uit.

### 18.5 Actieve sessies

De sessielijst toont:

- apparaat- of browsernaam;
- benaderde locatie indien toegestaan;
- aanmeldmethode;
- eerste aanmelding;
- laatste activiteit;
- huidige sessie-badge;
- actie **Sessie beëindigen**.

Er is een actie **Alle andere sessies beëindigen**, beschermd met step-up authenticatie.

### 18.6 Beveiligingsactiviteit

De gebruiker ziet een beperkte, begrijpelijke tijdlijn met succesvolle en mislukte aanmeldingen, registratie en verwijdering van methoden, herstelcodegebruik en sessie-intrekkingen. Gevoelige technische details worden niet getoond.

## 19. Step-up authenticatie in de UI

Bij een gevoelige actie verschijnt een compacte modale flow:

1. uitleg waarom extra bevestiging nodig is;
2. aanbevolen knop **Bevestigen met passkey**;
3. alternatief **Authenticator-code gebruiken**;
4. na succes automatische voortzetting van de oorspronkelijke actie.

De oorspronkelijke invoer of wizardstatus blijft behouden. De gebruiker hoeft na succesvolle verificatie niet opnieuw te beginnen.

Voorbeelden van gevoelige acties:

- authenticatiemethode toevoegen of verwijderen;
- herstelcodes genereren;
- beveiligingsbeleid wijzigen;
- rollen en rechten wijzigen;
- alle sessies intrekken;
- Site-migratie starten, hervatten of terugdraaien;
- gevoelige export genereren.

## 20. Foutmeldingen

Foutmeldingen zijn begrijpelijk, actiegericht, voorzien van referentiecode en bevatten geen secrets of stacktraces.

Authenticatiefouten gebruiken onder meer:

- **Aanmelden is niet gelukt. Controleer uw gegevens of gebruik een andere methode.**
- **De bevestiging is verlopen. Probeer opnieuw.**
- **Deze passkey is niet meer actief. Gebruik een andere methode.**
- **U hebt deze handeling geannuleerd.**
- **Voor deze actie is extra bevestiging nodig.**

## 21. Toegankelijkheid

Minimale eisen:

- volledige toetsenbordnavigatie;
- zichtbare focusstatus;
- voldoende kleurcontrast;
- labels voor formulieronderdelen;
- ondersteuning voor schermlezers;
- fouten niet uitsluitend met kleur aanduiden;
- schaalbare tekst;
- geen essentiële interacties uitsluitend via hover;
- TOTP-codes kunnen als één toegankelijk veld worden ingevoerd;
- QR-codes hebben een handmatig alternatief;
- Passkeyflows blijven bruikbaar wanneer een platformauthenticator niet beschikbaar is.

## 22. Rollen en schermrechten

De UI verbergt niet-toegestane acties, maar de backend blijft de definitieve autorisatie uitvoeren.

Organisatie- en systeembeheerders kunnen, volgens hun rechten:

- authenticatiebeleid raadplegen en wijzigen;
- authenticatiemethoden van gebruikers intrekken;
- gecontroleerd accountherstel starten;
- sessies intrekken;
- security-events raadplegen.

Beheerders kunnen nooit een bestaande Passkey of TOTP-code namens een gebruiker bekijken of exporteren.

## 23. Bevestigde ontwerpbeslissingen

- Overwegend witte interface met bedrijfsaccentkleuren.
- AI-vraagveld op het dashboard.
- Optionele gesproken AI-vragen.
- Altijd zichtbare feedback tijdens AI- en achtergrondverwerking.
- Volledig meertalige en lokalisatieklare interface.
- Centrale Naamgevingsservice als enige bron voor bestandsnamen.
- Bestandsnamen worden ook in batches één voor één gegenereerd.
- Bulkbevestigingen en latere steekproeven worden afzonderlijk beheerd.
- Tijdelijke Sites worden herkenbaar aangeduid.
- Migratie naar een definitief sitenummer gebeurt via simulatie en wizard.
- Sterke authenticatie ondersteunt TOTP en Passkeys.
- Passkeys zijn de aanbevolen methode.
- Biometrische aanmelding gebeurt via WebAuthn en niet via eigen biometrische opslag.
- Gebruikers kunnen meerdere Passkeys beheren, hernoemen en intrekken.
- Het verwijderen van de laatste bruikbare authenticatiemethode wordt geblokkeerd.
- Step-up authenticatie beschermt gevoelige acties.

## 24. Openstaande UI-beslissingen

- Definitieve bedrijfskleuren en design tokens.
- Definitief logoformaat en plaatsing.
- Initiële ondersteunde talen.
- Definitieve componentbibliotheek.
- Exacte mobiele schermprioriteiten.
- Of wachtwoordloze en usernameless Passkey-aanmelding bij de eerste release worden geactiveerd.
- Definitieve lijst van acties die step-up authenticatie vereisen.
- Of gebruikers een downloadbaar bestand met herstelcodes mogen genereren.