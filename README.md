# Kelvic-the-Artist-Webpage
Web page for BFB 321
Project Title and  Description:
Kelvic The Artist Websolution
An enterprise system for small independant artists without business background and no money for large ERP systems like SAP. We are using the small artist Kelvic the artist as a base to make this web solution.


| Group names |  student numbers|
|-------------|----------------|
|Siviwe Vilane | u24693180 |
|Kelley Thlamo | u24963357 |
|Snethemba Ndlovu | u24990150 |
|Kelebone Kgalaeng | u16068221 |


features
| Page |  What it does |
|-------------|----------------|
| overview/ | The Web solution woks as an ERP system as in connects the business operations to one database. It has modules such as production, logistics, orders, orders and storage. |
| /login | The login page aunthenticates if the user is the admin meant to access the web solution, it uses mySQL tables. |
| /index | The welcome page. Summarises data shown in each and every page and provides current status. |
| /production | Tracks the artists studio operations. It uses the database to show data such as monthly goals and cost efficiency |
| /logistics | The shipping manager. Uses EOQ and EPQ to provide insights to the user. |
| /orders | Handles demand and fulfilment. Shows historic demand and fulfilment and also takes new orders. |
| /orders/<id> | It allows the user to see a more detailed view of the individual order. |
| /storage | The storage of the business. Uses the EPQ/EOQ formulas to show the status of an SKU. |
| / |  |
| / |  |
| / |  |

Installation and setup instructions:
1. Install Python and git on your device: https://git-scm.com/
2. Clone the repository:

   git clone [https://github.com/u24963357-lgtm/Kelvic-the-Artist-Webpage]
   cd Kelvic-the-Artist-Webpage

3. Configure the database connection values in a local `.env` file. Start from the example:
   - On first setup only, if `.env` does not already exist: `Copy-Item .env.example .env`
   - Edit `.env` and set `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`. Set a long, random `FLASK_SECRET_KEY`; do not commit `.env`.

   In the repository terminal, run:
   - `python -m venv venv`
   - `.\venv\Scripts\Activate.ps1`
   - `pip install -r requirements.txt`
   - `python -c "from db import connect; c = connect(); c.close(); print('Database connection OK')"` to verify the connection
   - `python init_db.py` to create/update the tables and load sample data when the database is empty
   - `python app.py`

4. Open your browser and go to http://127.0.0.1:5000/

5. Log in information:
       username :adminA  password : Kelvic_2026A
       username :adminB  password : Kelvic_2026B
