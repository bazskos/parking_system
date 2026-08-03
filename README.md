# Parkolóhely-foglalás API

Készítette: Kiss Balázs

Ez a projekt egy robusztus, konténerizált backend szolgáltatás parkolóhelyek kezeléséhez és foglalásához. A rendszer egyetlen paranccsal, Docker segítségével indítható, és induláskor automatikusan inicializálja az adatbázist a teszteléshez szükséges referenciaadatokkal.

---

## 1. Rendszerterv (Architektúra)

A megoldás egy modern, mikroszolgáltatás-jellegű architektúrára épül, amely a következő technológiai stacket használja:
*   **Backend keretrendszer:** Python (FastAPI) – A kiemelkedő teljesítmény és az automatikus OpenAPI (Swagger) dokumentáció miatt.
*   **Adatbázis:** PostgreSQL – A relációs adatmodell és a stabil dátum/idő intervallum vizsgálatok (overlap) biztosítása érdekében.
*   **ORM:** SQLAlchemy – Az adatbázis-műveletek és a Python objektumok közötti absztrakcióhoz.
*   **Infrastruktúra:** Docker & Docker Compose – A környezetfüggetlen, izolált futtatáshoz.

### Adatmodell logikája
A rendszer két fő entitásra épül:
1.  **ParkingSpot (Parkolóhely):** Tartalmazza a parkolóhely azonosítóját, nevét és opcionálisan a típusát (pl. "normal", "vip", "disabled"). 
    *   *Szervezési elv:* Szándékosan nem tartalmaz `is_free` (szabad-e) boolean mezőt. A parkolóhelyek elérhetősége az idő függvényében folyamatosan változik, így a "szabad" státuszt a rendszer dinamikusan, a foglalások lekérdezésével és az ütközések (overlap) vizsgálatával kalkulálja ki a háttérben.
2.  **Booking (Foglalás):** Nyilvántartja a lefoglalt parkolóhelyet (Foreign Key), a kérelmező nevét, valamint a foglalás pontos kezdő és záró időpontját.

---

## 2. Felhasználói Kézikönyv (Telepítés és Futtatás)

Előfeltétel: A futtatáshoz telepített **Docker** és **Docker Compose** szükséges.

### Indítás lépései:
1.  Nyiss egy terminált a projekt gyökérmappájában.
2.  Add ki a következő parancsot a konténerek felépítéséhez és elindításához (háttérben futtatva):

    docker compose up --build -d

3.  A rendszer indításakor a backend automatikusan felépíti a PostgreSQL táblákat.
4.  **Adatbázis inicializálása:** Ha a parkolóhelyek táblája üres, a rendszer induláskor automatikusan feltölti 5 darab alapértelmezett parkolóhellyel (3 normál, 1 VIP, 1 mozgássérült), így az API azonnal tesztelhető kézi adatbevitel nélkül.

### Leállítás:
A szolgáltatások leállításához és a konténerek eltávolításához használd a következő parancsot:

    docker compose down

*(Megjegyzés: A parancs futtatása után a PostgreSQL adatbázis adatai a Docker volume-nak köszönhetően megmaradnak. Ha teljesen tiszta lappal szeretnéd újraindítani a rendszert, használd a `docker compose down -v` parancsot.)*

---

## 3. API-leírás (Végpontok)

A FastAPI egyik legnagyobb előnye, hogy a megírt Pydantic sémák alapján valós időben generálja az OpenAPI (Swagger UI) specifikációt. 

Amikor a Docker konténerek futnak, a teljes, interaktív API dokumentáció és a tesztkörnyezet elérhető a böngészőből ezen a címen:
👉 **http://127.0.0.1:8000/docs**

### Elérhető főbb műveletek:
*   `GET /spots` - Az összes elérhető parkolóhely lekérdezése (alapértelmezett lista).
*   `POST /bookings` - Új foglalás leadása. A rendszer automatikusan validálja a kezdő/záró dátumokat, és visszautasítja a kérést (400 Bad Request), ha a megadott időintervallumban a parkolóhely már foglalt.
*   `GET /spots/{spot_id}/bookings` - Egy adott parkolóhelyhez tartozó összes foglalás lekérdezése.
*   `DELETE /bookings/{booking_id}` - Egy már létező foglalás törlése/lemondása az azonosítója alapján.