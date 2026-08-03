# Döntési Napló és Reflexió

Készítette: Kiss Balázs  

---

## 1. Döntési Napló

### 1. Adatbázis technológia kiválasztása
* **Döntés:** PostgreSQL adatbázis használata.
* **Indoklás:** A feladat kulcsfontosságú eleme az időpont-ütközések (overlap) vizsgálata. A relációs adatbázisok natív dátum- és időkezelése, valamint az SQL-alapú szűrések biztosítják a legstabilabb, legpontosabb és legszervezettebb adatelérést ehhez a logikához.

### 2. Parkolóhelyek státuszának kezelése (Nincs `is_free` mező)
* **Döntés:** A `ParkingSpot` tábla nem tartalmaz statikus "szabad" (`is_free`) booleán mezőt.
* **Indoklás:** Egy parkolóhely elérhetősége dinamikusan változik az idő függvényében (lehet, hogy kedden szabad, de csütörtökön foglalt). Ha statikus mezőt használnánk, az adatinzisztenciához vezetne. Ehelyett a rendszer a meglévő foglalások és a megadott idősávok összevetésével valós időben számolja ki az ütközéseket.

### 3. Automatikus adatbázis-inicializálás
* **Döntés:** Az alkalmazás indulásakor lefutó Python-logika (`init_db()`) hozza létre a kezdeti parkolóhelyeket, ha a tábla üres.
* **Indoklás:** Ezzel elkerülhető, hogy a tesztelőnek külön manuális SQL parancsokat vagy seed szkripteket kelljen futtatnia a tesztelés megkezdése előtt; a rendszer azonnal működőképes állapotban indul.

### 4. Konténerizáció és portkezelés
* **Döntés:** A teljes projekt Docker Compose alapú futtatása, az adatbázis külső portjának `5433`-ra állításával.
* **Indoklás:** Ez garantálja a környezetfüggetlenséget ("mindenhol ugyan úgy fut"), miközben elkerüli a fejlesztői gépen esetleg már futó natív PostgreSQL instance-ok okozta portütközéseket.

---

## 2. Reflexió a fejlesztési folyamatról

A projekt megvalósítása során a FastAPI keretrendszer és az SQLAlchemy ORM kombinációja rendkívül hatékonynak bizonyult. A fejlesztés legnagyobb tanulsága a technológiai stackek (Docker vs. lokális környezet) közötti hálózati elérések és portok pontos konfigurálásának fontossága volt (pl. a lokális `localhost` átállítása konténer nevére, illetve az 5432/5433 portkonfliktus elhárítása). 

A feladat iteratív, kis lépésekben történő építkezése (váz -> adatbázis -> alap végpontok -> ütközésvizsgálat -> jogosultságok -> Docker) lehetővé tette, hogy minden egyes fázisban azonnal tesztelni tudjam a működést, így egy stabil, produkciós szintű backend sémát sikerült létrehozni.