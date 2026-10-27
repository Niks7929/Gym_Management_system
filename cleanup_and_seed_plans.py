"""
SETFIT DARK RAGE - Membership Plans Cleanup and Canonical Seeder
Safely updates, dedupes, and configures the exact 6 official membership plans.
"""
from app import create_app
from app.extensions import db
from app.models.membership import MembershipPlan, Membership, Payment

app = create_app()

OFFICIAL_PLANS = [
    {
        'name': 'Monthly Plan',
        'price': 1600.0,
        'duration_months': 1,
        'duration_days': 30,
        'description': 'Essential monthly access for focused training routines.',
        'features': [
            'Unlimited Gym Access',
            'Fitness Assessment',
            'Trainer Support',
            'Digital Workout Dashboard'
        ]
    },
    {
        'name': 'Quarterly Plan',
        'price': 4200.0,
        'duration_months': 3,
        'duration_days': 90,
        'description': 'Quarterly commitment designed for consistent hypertrophy and strength.',
        'features': [
            'Unlimited Gym Access',
            'Fitness Assessment',
            'Trainer Support',
            'Workout & Diet Tracking'
        ]
    },
    {
        'name': 'Half-Yearly Plan',
        'price': 7000.0,
        'duration_months': 6,
        'duration_days': 180,
        'description': '6-month intensive plan including locker room and biometric scans.',
        'features': [
            'Unlimited Gym Access',
            'Locker Access',
            'Trainer Support',
            'InBody Body Scan'
        ]
    },
    {
        'name': 'Yearly Plan',
        'price': 12000.0,
        'duration_months': 12,
        'duration_days': 365,
        'description': 'Complete annual transformation package with personal training sessions.',
        'features': [
            'Unlimited Gym Access',
            'Fitness Assessment',
            'Trainer Support',
            'Workout & Diet Dashboard',
            '2 PT Sessions'
        ]
    },
    {
        'name': 'Premium Annual VIP',
        'price': 18000.0,
        'duration_months': 12,
        'duration_days': 365,
        'description': 'Elite VIP tier with personal coach support, dedicated locker, and luxury recovery.',
        'features': [
            'Unlimited Gym Access',
            'Personal Trainer Support',
            'Digital Workout & Diet Dashboard',
            'Locker Access',
            'Premium Facilities'
        ]
    },
    {
        'name': 'Weekend Special',
        'price': 3500.0,
        'duration_months': 3,
        'duration_days': 90,
        'description': 'Flexible access for weekend and evening powerlifters and athletes.',
        'features': [
            'Weekend & Evening Access',
            'Trainer Support',
            'Digital Check-in Pass',
            'Locker Access'
        ]
    }
]

def cleanup_and_seed():
    with app.app_context():
        print("[*] Inspecting existing plans...")
        existing_plans = MembershipPlan.query.all()
        print(f"[*] Found {len(existing_plans)} plan records in database.")
        
        canonical_map = {} # name -> plan obj

        # First, ensure canonical plans exist or update them
        for pdata in OFFICIAL_PLANS:
            # Check by exact name or legacy names
            legacy_names = [pdata['name']]
            if pdata['name'] == 'Monthly Plan':
                legacy_names.extend(['BASIC', 'Monthly', 'Monthly Plan Updated'])
            elif pdata['name'] == 'Quarterly Plan':
                legacy_names.extend(['STANDARD', 'Quarterly'])
            elif pdata['name'] == 'Premium Annual VIP':
                legacy_names.extend(['PREMIUM', 'Premium Annual VIP - ₹18,000', 'Premium Annual VIP'])
            elif pdata['name'] == 'Yearly Plan':
                legacy_names.extend(['ELITE', 'Yearly'])

            plan = MembershipPlan.query.filter(MembershipPlan.name.in_(legacy_names)).first()
            if not plan:
                plan = MembershipPlan(
                    name=pdata['name'],
                    price=pdata['price'],
                    duration_months=pdata['duration_months'],
                    duration_days=pdata['duration_days'],
                    description=pdata['description'],
                    is_active=True
                )
                plan.set_features(pdata['features'])
                db.session.add(plan)
                db.session.flush()
                print(f"[+] Created canonical plan: {plan.name} (ID: {plan.id})")
            else:
                # Update attributes
                plan.name = pdata['name']
                plan.price = pdata['price']
                plan.duration_months = pdata['duration_months']
                plan.duration_days = pdata['duration_days']
                plan.description = pdata['description']
                plan.set_features(pdata['features'])
                plan.is_active = True
                print(f"[~] Updated canonical plan: {plan.name} (ID: {plan.id})")
            
            canonical_map[pdata['name']] = plan

        db.session.commit()

        # Re-fetch canonical plan IDs
        canonical_ids = {p.id for p in canonical_map.values()}
        default_canonical_id = canonical_map['Monthly Plan'].id
        vip_canonical_id = canonical_map['Premium Annual VIP'].id

        # Re-map any duplicate/stray plans
        all_plans = MembershipPlan.query.all()
        for p in all_plans:
            if p.id not in canonical_ids:
                print(f"[*] Found duplicate/stray plan: ID {p.id} ({p.name})")
                target_id = vip_canonical_id if 'PREMIUM' in p.name.upper() or 'VIP' in p.name.upper() else default_canonical_id
                
                # Re-map memberships
                mems = Membership.query.filter_by(plan_id=p.id).all()
                for m in mems:
                    m.plan_id = target_id
                
                # Delete duplicate plan safely
                db.session.delete(p)
                print(f"[-] Deleted duplicate plan ID {p.id} after re-mapping {len(mems)} memberships.")

        db.session.commit()
        
        # Verify result
        active_plans = MembershipPlan.query.filter_by(is_active=True).order_by(MembershipPlan.price.asc()).all()
        print(f"\n[+] SUCCESS! Total Active Plans in Database: {len(active_plans)}")
        for ap in active_plans:
            print(f"    - ID: {ap.id} | {ap.name} | ₹{ap.price:,.0f} | {ap.duration_months} mo | Features: {len(ap.features_list)}")

if __name__ == '__main__':
    cleanup_and_seed()
