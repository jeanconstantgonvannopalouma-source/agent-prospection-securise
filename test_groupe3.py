import sys
import asyncio
sys.path.insert(0, 'src')

from modules.prospect_finder import prospect_finder
from modules.message_engine import message_engine
from modules.analytics import analytics
from database.connection import init_db
from database.repositories import ProspectRepository
from database.models import ProspectStatus
from config import config

print('\n')
print('🧪 TEST GROUPE 3: MODULES MÉTIER')
print('==================================\n')

print('1️⃣ Test ProspectFinder...')
async def test_finder():
    results = await prospect_finder.search_prospects({'limit': 3})
    assert len(results) > 0
    print(f'   ✓ {len(results)} prospects trouvés')
    return results

results = asyncio.run(test_finder())

print('2️⃣ Test enrichissement...')
async def test_enrich():
    prospect_data = results[0]
    enriched = await prospect_finder.enrich_prospect(prospect_data)
    assert enriched is not None
    assert 'first_name' in enriched
    assert 'qualification_score' in enriched
    score = enriched['qualification_score']
    print(f'   ✓ Prospect enrichi (score: {score}/100)')

asyncio.run(test_enrich())

print('3️⃣ Test MessageEngine...')
db = init_db(config.DATABASE_URL)
session = db.get_session()
repo = ProspectRepository(session)
prospect = repo.get_all(limit=1)[0] if repo.count() > 0 else None

if prospect:
    message = message_engine.generate_personalized_message(
        prospect=prospect,
        pain_points=['Acquisition difficile'],
        solution='Notre plateforme IA',
        tone='professionnel'
    )
    assert message is not None
    print(f'   ✓ Message généré ({len(message)} caractères)')
    
    quality = message_engine.analyze_message_quality(message)
    print(f'   ✓ Qualité: {quality["quality_score"]}/100')
else:
    print('   ⚠️ Pas de prospect en BD')

db.close_session(session)

print('4️⃣ Test Analytics...')
db = init_db(config.DATABASE_URL)
stats = analytics.get_dashboard_stats(db, ProspectRepository, ProspectStatus)
assert 'total_prospects' in stats
print(f'   ✓ Stats: {stats}')

print()
print('✅ GROUPE 3 RÉUSSI - MODULES MÉTIER 100% OPÉRATIONNELS!')
print()
