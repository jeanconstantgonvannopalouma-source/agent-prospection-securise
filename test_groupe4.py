import sys
from pathlib import Path

# Ajoute le chemin src
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import asyncio

print('\n')
print('🧪 TEST GROUPE 4: CORE & API')
print('=============================\n')

print('1️⃣ Test imports...')
try:
    from database.connection import init_db
    from database.repositories import ProspectRepository
    from database.models import ProspectStatus
    print('   ✓ Database imports OK')
except Exception as e:
    print(f'   ❌ Erreur database: {e}')
    sys.exit(1)

try:
    from modules.message_engine import message_engine
    print('   ✓ Message engine OK')
except Exception as e:
    print(f'   ❌ Erreur message: {e}')
    sys.exit(1)

try:
    from modules.analytics import analytics
    print('   ✓ Analytics OK')
except Exception as e:
    print(f'   ❌ Erreur analytics: {e}')
    sys.exit(1)

print('\n2️⃣ Test API Routes...')
try:
    from api.routes import api_routes
    print('   ✓ API routes OK')
except Exception as e:
    print(f'   ❌ Erreur API: {e}')
    sys.exit(1)

print('\n3️⃣ Test API - Create Prospect...')
try:
    result, status = api_routes.create_prospect({
        'first_name': 'API',
        'last_name': 'Test',
        'email': 'api.test2@example.com',
        'company': 'APITestCorp',
        'job_title': 'CTO'
    })
    assert status == 201
    prospect_id = result.get('prospect_id', 'unknown')
    print(f'   ✓ Prospect créé (ID: {prospect_id})')
except Exception as e:
    print(f'   ❌ Erreur création: {e}')
    sys.exit(1)

print('\n4️⃣ Test API - List Prospects...')
try:
    result, status = api_routes.list_prospects(limit=10)
    assert status == 200
    total = result['total']
    print(f'   ✓ Listage: {total} prospects au total')
except Exception as e:
    print(f'   ❌ Erreur listage: {e}')
    sys.exit(1)

print('\n5️⃣ Test API - Health Check...')
try:
    result, status = api_routes.health_check()
    assert status == 200
    health_status = result.get('status', 'unknown')
    print(f'   ✓ Health: {health_status}')
except Exception as e:
    print(f'   ❌ Erreur health: {e}')
    sys.exit(1)

print('\n6️⃣ Test API - Stats...')
try:
    result, status = api_routes.get_stats()
    assert status == 200
    stats = result['stats']
    total_prospects = stats.get('total_prospects', 0)
    print(f'   ✓ Stats: {total_prospects} prospects')
except Exception as e:
    print(f'   ❌ Erreur stats: {e}')
    sys.exit(1)

print('\n')
print('✅ GROUPE 4 RÉUSSI - API 100% OPÉRATIONNELLE!')
print()
