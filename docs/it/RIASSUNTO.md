# aeoi - Riassunto per le associazioni e i loro membri

Stato: settembre 2026. Per fiduciarie, trust company, family office e gestori patrimoniali che
trasmettono all'AFC le comunicazioni SAI (CRS) per i propri veicoli. Una pagina; i riferimenti
tecnici sono nelle pagine tedesche `docs/de/WAS-AENDERT-SICH-MIT-3.0.md` e `docs/de/ANLEITUNG.md`.
Le citazioni sono tratte dall'edizione italiana della Direttiva tecnica dell'AFC (settembre 2026).

## Di cosa si tratta

Le comunicazioni per l'anno 2026 (termine 30 giugno 2027, art. 15 cpv. 1 LSAI) sono le prime che
devono essere create nel nuovo schema OCSE CRS 3.0. Il portale dell'AFC: «Fino al 14.12.2026 è
supportata solo la versione 2.0. Dal 16.1.2027 è supportata solo la versione 3.0.» (Direttiva
tecnica, numero 5.3.1). Lo schema 3.0 richiede per ogni conto nuove indicazioni obbligatorie
(autocertificazione, procedura di adeguata verifica, tipo di conto, tipo delle persone che
esercitano il controllo); un file con la vecchia struttura sarà respinto da gennaio. Chi finora
creava le comunicazioni con il modulo online o con uno script proprio deve adattare il processo.

## Cos'è aeoi

`aeoi` è uno strumento aperto (Apache-2.0, codice sorgente consultabile) che crea il file CRS-XML
da una tabella Excel e lo verifica **prima** del caricamento, come fa il portale:

- schema OCSE 2.0 e 3.0, set di caratteri, Stati partner dell'anno di comunicazione, cifre di
  controllo IBAN/ISIN;
- 59 delle 65 regole della Direttiva tecnica, con il codice di errore e il testo dell'AFC. Le
  altre sei (trasporto, decifratura, antivirus, registrazione dell'istituto) può verificarle
  solo il portale;
- crittografia e impacchettamento secondo il numero 3.3.1, comunicazioni test con i contrassegni
  corretti;
- un registro locale delle comunicazioni inviate, così che correzioni e annullamenti abbiano i
  riferimenti giusti (numero 6), anche attraverso il passaggio dalla 2.0 alla 3.0;
- lettura della risposta del portale: ogni codice viene spiegato.

Chi non vuole installare nulla verifica un file XML esistente o un modello compilato su una
pagina web, direttamente nel browser, in italiano, francese o tedesco. Il file non lascia il
browser.

## Cosa aeoi non è

Nessun caricamento: l'istituto carica il pacchetto da sé nel portale SAI, come oggi. Nessuna
consulenza sull'obbligo di comunicazione o sulla classificazione dei conti. Nessuna garanzia
prima del progetto pilota: lo strumento è costruito sugli schemi pubblicati e sulla Direttiva
tecnica ed è coperto da 187 test automatici, ma solo una comunicazione test attraverso il portale
mostra se l'AFC legge i file allo stesso modo.

## Protezione dei dati

Tutto gira sul computer dell'istituto; i dati dei conti non lo lasciano. La pagina web non ha
server, analytics né registro degli accessi; una regola di sicurezza nel browser impedisce che
dopo la scelta del file venga contattato qualsiasi indirizzo. Lo strumento non richiede
registrazione e non invia nulla a nessuno.

## Costi

Lo strumento è e resta gratuito. È previsto un abbonamento di supporto **per organizzazione**,
non per utente, con numero illimitato di istituti tenuti alla comunicazione: 900 CHF/anno fino a
10 veicoli, 1'500 fino a 50, 2'400 oltre; software house 2'500 CHF/anno. Gli istituti pilota
non pagano nulla durante il progetto pilota.

## Cosa cerchiamo ora: da uno a tre istituti pilota

Un istituto finanziario tenuto alla comunicazione, registrato, con accesso alle comunicazioni
test del portale SAI, che

1. a novembre 2026 carichi una comunicazione test nello schema 2.0 (verifica il percorso di
   trasporto: crittografia, pacchetto, identificativi),
2. nella settimana del 16 gennaio 2027 carichi una comunicazione test nello schema 3.0,
3. ci comunichi poi solo i codici e gli identificativi della conferma di validazione del
   portale - mai il file, mai dati dei conti.

Impegno: circa un'ora per comunicazione test. Le comunicazioni test vengono validate dal
portale, non inoltrate, e «sono cancellate una volta alla settimana, durante la notte tra sabato e
domenica» (numero 5.3.5). Le domande aperte sulla prassi dell'AFC, a cui il pilota risponde,
sono in `docs/OPEN-QUESTIONS.md`.

Contatto: <nome, e-mail> - Codice sorgente e guida: https://github.com/aeoi-com/aeoi - Verifica nel browser: https://aeoi-com.github.io/aeoi/
