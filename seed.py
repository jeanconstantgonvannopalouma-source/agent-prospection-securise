import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Prospect(Base):
    __tablename__ = "prospects"
    id      = Column(Integer, primary_key=True)
    name    = Column(String)
    email   = Column(String, unique=True)
    company = Column(String)
    status  = Column(String, default="nouveau")

database_url = os.getenv("DATABASE_URL")
engine  = create_engine(database_url)
Session = sessionmaker(bind=engine)
db      = Session()

prospects = [
    ("Marc Vasseur",     "marc@vasseur-seo.fr",          "Vasseur SEO (Freelance)",          "nouveau"),
    ("Julie Faure",      "julie@faure-design.com",        "Studio Faure (Freelance UI/UX)",   "nouveau"),
    ("Thomas Renard",    "thomas@renard-dev.io",          "Renard Code (Développeur)",        "nouveau"),
    ("Cédric Morel",     "cedric@digital-pulse.fr",       "Digital Pulse (Agence Web)",       "nouveau"),
    ("Sarah Benali",     "sarah@payflow.io",              "PayFlow (Startup SaaS)",           "nouveau"),
    ("Pierre Lemaire",   "pierre@les-ptits-bouchons.org", "Les P'tits Bouchons (Asso)",       "nouveau"),
    ("Hélène Moreau",    "helene@moreau-coaching.com",    "Moreau Coaching",                  "nouveau"),
    ("Nicolas Garnier",  "nicolas@bistrot-deco.fr",       "Bistrot Déco (E-commerce)",        "nouveau"),
    ("Lucas Bernard",    "lucas@lucas-media.fr",          "Lucas Media (Créateur contenu)",   "nouveau"),
    ("Élodie Petit",     "elodie@le-comptoir-bio.fr",     "Le Comptoir Bio (Commerce)",       "nouveau"),
    ("Alexandre Leroy",  "alex@learnflow.io",             "LearnFlow (Startup EdTech)",       "nouveau"),
    ("Marie Dupuis",     "marie@as-basket-lyon.fr",       "AS Basket Lyon (Association)",     "nouveau"),
    ("Antoine Girard",   "antoine@girard-rh.com",         "Girard Conseil (Consultant RH)",   "nouveau"),
    ("Laura Blanc",      "laura@blanc-rp.fr",             "Blanc RP (Agence de com)",         "nouveau"),
    ("Maxime Roux",      "maxime@app-craft.fr",           "App Craft (Développeur Mobile)",   "nouveau"),
    ("Chloé Mercier",    "chloe@chloemercier.design",     "Studio Mercier (Brand Designer)",  "nouveau"),
    ("Romain David",     "romain@com-impact.fr",          "Com Impact (Petite Agence)",       "nouveau"),
    ("David Rousseau",   "david@solidaires-monde.org",    "Solidaires Monde (ONG)",           "nouveau"),
    ("Manon Bonnet",     "manon@coaching-fit.fr",         "Fit Coaching",                     "nouveau"),
    ("Quentin Faivre",   "quentin@neural-boost.io",       "Neural Boost (Startup IA)",        "nouveau"),
]

try:
    print("🚀 Ajout des 20 prospects...")
    for name, email, company, status in prospects:
        exists = db.query(Prospect).filter_by(email=email).first()
        if not exists:
            db.add(Prospect(name=name, email=email, company=company, status=status))
    db.commit()
    print("✅ Les 20 prospects ont été ajoutés avec succès !")
except Exception as e:
    db.rollback()
    print(f"❌ Erreur : {e}")
finally:
    db.close()
