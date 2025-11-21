"""
Initialize Default Alert Rules
"""

from app import create_app, db
from app.models import AlertRule
from app.alerts import DEFAULT_ALERT_RULES


def init_default_rules():
    """Inicjalizuje domyślne reguły alertów dla wszystkich monitorowanych miast"""
    
    app = create_app()
    
    with app.app_context():
        # Pobierz wszystkie monitorowane miasta z collector
        cities = ["Warszawa", "Yakutsk"]  # Można rozszerzyć
        
        print("🔧 Initializing default alert rules...")
        
        for city in cities:
            print(f"\n Creating rules for {city}:")
            
            for rule_template in DEFAULT_ALERT_RULES:
                # Sprawdź czy reguła już istnieje
                existing = AlertRule.query.filter_by(
                    city=city,
                    name=rule_template['name'],
                    condition_type=rule_template['condition_type']
                ).first()
                
                if existing:
                    print(f"   ⏭  Skipping '{rule_template['name']}' - already exists")
                    continue
                
                # Utwórz nową regułę
                rule = AlertRule(
                    name=rule_template['name'],
                    city=city,
                    condition_type=rule_template['condition_type'],
                    operator=rule_template['operator'],
                    threshold=rule_template['threshold'],
                    is_active=True
                )
                
                db.session.add(rule)
                print(f"   ✓ Created: {rule_template['name']}")
        
        db.session.commit()
        print("\n All default alert rules initialized!")


if __name__ == '__main__':
    init_default_rules()