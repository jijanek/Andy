# Andy — diagnostický příjem úkolů

GitHub Actions poslouchá událost `issues.labeled` v `jijanek/Andy`. Job přijme
pouze přesný štítek `andy-task` a označení od vlastníka `jijanek` (GitHub ID
`323095460`). Kontroluje identitu, která štítek skutečně přidala, i identitu,
která požádala o nový běh. Autor Issue může být kdokoli. Ověřený vlastník
přidáním štítku potvrzuje zařazení Issue do fronty.

Job používá jen `issues: write`, které potřebuje pro čtení aktuálního Issue,
kontrolu potvrzení a zápis jednoho komentáře s odkazem na Actions run.
Obsah zadání se nečte pro účely diagnostiky ani se nevypisuje do logu.
Workflow nenačítá checkout, nevyžaduje tajnou hodnotu a nespouští AI.

Běhy pro jedno Issue se řadí do stejné fronty bez rušení rozběhnutého jobu.
Různá Issues mají vlastní fronty. Deduplikace uznává pouze potvrzení s přesným
markerem od účtu `github-actions[bot]` (ID `41898282`). Po úspěšném zápisu je
opakovaný běh nebo opětovné přidání stejného štítku přeskočeno. Smazání původního
potvrzení odstraní záznam deduplikace. Pokud se štítek mezitím odstraní, kontrola
aktuálního stavu čekající událost přeskočí. Odebrání štítku může těsně po kontrole
stavu předběhnout zápis diagnostiky. Fronta má limit 100 čekajících jobů na Issue.

## Test po schváleném mergi

GitHub vyžaduje workflow na výchozí větvi. Před mergem lze spustit místní testy,
živá událost přidání štítku však tuto větev nespustí.

1. V Issues vytvoř dvě testovací Issues bez údajů, které nemají být veřejné.
   Pro test připrav repozitářové štítky `andy-task` a například `andy-diagnostic-control`,
   pokud ještě neexistují.
2. Jako `jijanek` přidej k prvnímu Issue kontrolní štítek. Job v Actions má být
   přeskočený a v Issue nemá vzniknout potvrzení.
3. Pokud máš už teď jiného spolupracovníka s právem označovat Issues, ať přidá
   `andy-task` k prvnímu Issue. Job má být přeskočený. Poté štítek odeber.
   Pokud takový účet nemáš, použij simulaci v místních testech.
4. Jako `jijanek` přidej `andy-task` k prvnímu Issue. V Actions otevři běh
   **Andy issue trigger (diagnostic)** a ověř hlášku `Accepted`. V Issue ověř
   právě jeden komentář od GitHub Actions s odkazem na tento běh.
5. Odeber `andy-task` z prvního Issue a přidej ho znovu. Job má skončit hláškou
   `Duplicate` a počet potvrzení zůstat stejný.
6. Pro ověření souběhu opakuj několik rychlých cyklů odebrat/přidat na stejném
   Issue a nezávisle označ druhé Issue. První Issue má stále jedno potvrzení,
   druhé získá vlastní. V Actions ověř, že se joby stejného Issue nepřekrývaly,
   pokud se podařilo frontu zaplnit dříve, než první job doběhl.

Místní test spustíš příkazem `python3 -m unittest discover -s .github/tests -v`.
Vyžaduje PyYAML a Node.js 24. Vykoná skutečný skript z workflow s imitovaným
GitHub API a kontroluje deklaraci fronty. Pořadí a doručení živých jobů ověřuje
až test na výchozí větvi.

## Pozdější připojení executoru

Executor je samostatná, výslovně schvalovaná změna:

1. Zachovej kontrolu důvěryhodné identity a serializaci po Issue. Pro zadávání
   přes Aju nejprve ověř, jakou identitu používá autorizovaný konektor v události.
   Případně schval konkrétní GitHub App identitu a uprav seznam důvěryhodných
   účtů. Pro executor zaveď vlastní záznam stavu s možností bezpečného opakování
   při selhání. Diagnostické potvrzení nevyjadřuje dokončení vývoje.
2. Spusť oficiální Codex Action na standardním Linux runneru. Předej schválený
   projektový klíč z GitHub Secrets pouze kroku s Codexem. Použij checkout
   konkrétní důvěryhodné revize bez uložených GitHub credentials, `contents: read`
   a sandbox `workspace-write`. Přečti `AGENTS.md` a předávej obsah Issue jako
   data, nikoli shellový vstup.
3. Samostatně spusť testy. V odděleném jobu bez OpenAI klíče ověř a publikuj
   omezený diff na pracovní větvi, otevři PR jen s jasně schválenými GitHub
   oprávněními a připoj výsledek k Issue. Job se zapisovacím tokenem nevykonává
   kód z kandidátní změny. Merge a deploy čekají na Jirku.
