# Kelvic-the-Artist-Webpage
Web page for BFB 321
Project Title and  Description:
Kelvic The Artist Websolution
An enterprise system for small independant artists without business background and no money for large ERP systems like SAP. We are using the small artist Kelvic the artist as a base to make this web solution.


Group names and student numbers:
Siviwe Vilane u24693180
Kelley Thlamo u24963357
Snethemba Ndlovu u24990150
Kelebone Kgalaeng  u16068221

Installation and setup instructions:
1. Install Python and git on your device: https://git-scm.com/
2. Clone the repository:

   git clone [https://github.com/u24963357-lgtm/Kelvic-the-Artist-Webpage]
   cd Kelvic-the-Artist-Webpage

3. Configure the database connection values in a local `.env` file (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`). In the repository terminal, run:
   - `python -m venv venv`
   - `.\venv\Scripts\Activate.ps1`
   - `pip install -r requirements.txt`
   - `python init_db.py` to create the tables and load sample data when the database is empty
   - `python app.py`

4. Open your browser and go to http://127.0.0.1:5000/

5. Log in information:
       username :adminA  password : Kelvic_2026A
       username :adminB  password : Kelvic_2026B
