#!/usr/bin/env python3

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.guild import Guild, GuildRelationship
from app.models.district import District

def init_guilds():
    app = create_app()
    
    with app.app_context():
        # Check if guilds already exist
        existing_guilds = Guild.query.count()
        if existing_guilds > 0:
            print(f"✅ Found {existing_guilds} existing guilds. Skipping initialization.")
            return
        
        # Find district IDs for headquarters
        greywater_district = District.query.filter_by(name='Greywater').first()
        goldmark_district = District.query.filter_by(name='Goldmark (5th)').first()
        
        # Create the initial guilds with campaign data
        guilds_data = [
            {
                'name': 'The Dockers\' Brotherhood',
                'leadership': '"Iron Tam" Blackwater - Gruff halfling who commands absolute loyalty from the waterfront workers',
                'description': 'Controls all shipping, loading, and riverside activities around the dark mere and remaining canals.',
                'headquarters_district_id': greywater_district.id if greywater_district else None,
                'status': 'Active',
                'influence': 'High'
            },
            {
                'name': 'The Healers\' Circle',
                'leadership': 'High Physician Elena Brightmend - Human cleric whose powers have notably NOT diminished since The Weeping',
                'description': 'Runs most medical facilities throughout the city and has significant moral authority. Not associated with any single district.',
                'headquarters_district_id': None,  # No specific district
                'status': 'Active',
                'influence': 'High'
            },
            {
                'name': 'The Merchants\' Consortium',
                'leadership': 'Guildmaster Valeria Ashford - A pragmatic woman in her 50s who survived The Weeping by pivoting from magical goods to mundane trade',
                'description': 'Controls most legitimate trade in and out of the city. Also serves as the District Warden for the Goldmark District.',
                'headquarters_district_id': goldmark_district.id if goldmark_district else None,
                'status': 'Active',
                'influence': 'High'
            },
            {
                'name': 'The Artificers\' Union',
                'leadership': 'Master Engineer Korven Ironwright - Dwarven craftsman who\'s embraced steam technology since magic became unreliable',
                'description': 'Controls most mechanical infrastructure, workshops, and the few functioning steam-powered systems throughout the city.',
                'headquarters_district_id': goldmark_district.id if goldmark_district else None,
                'status': 'Active',
                'influence': 'Medium'
            },
            {
                'name': 'The Watchers\' Guild',
                'leadership': 'Captain Marcus Greymantle - Former military officer who organized civilian security after the city watch was overwhelmed',
                'description': 'Supplements the official watch, patrols safer districts, and maintains specialized investigators and "heavy watchmen" for serious crimes. Has ongoing tensions with District Wardens over jurisdiction and authority, particularly with Captain Shea of Greywater District who ignores the warden structure entirely.',
                'headquarters_district_id': None,
                'status': 'Active',
                'influence': 'High'
            }
        ]
        
        # Create guilds
        guilds = []
        for guild_data in guilds_data:
            guild = Guild(**guild_data)
            db.session.add(guild)
            guilds.append(guild)
        
        db.session.commit()  # Commit to get guild IDs
        
        # Create the Artificers vs Merchants relationship
        artificers = Guild.query.filter_by(name='The Artificers\' Union').first()
        merchants = Guild.query.filter_by(name='The Merchants\' Consortium').first()
        
        if artificers and merchants:
            relationship = GuildRelationship(
                guild_1_id=artificers.id,
                guild_2_id=merchants.id,
                relationship_type='negative',
                description='Both guilds are headquartered in the Goldmark District, but the Merchants\' Consortium holds political advantage as Guildmaster Valeria Ashford also serves as the District Warden, creating tension over territorial control and influence.'
            )
            db.session.add(relationship)
        
        try:
            db.session.commit()
            print(f"✅ Created {len(guilds_data)} guilds successfully!")
            
            # List created guilds
            for guild in Guild.query.all():
                print(f"   - {guild.name}")
                print(f"     Leader: {guild.leadership}")
                if guild.headquarters:
                    print(f"     Headquarters: {guild.headquarters.name}")
                print()
            
            # List relationships
            relationships = GuildRelationship.query.all()
            if relationships:
                print("✅ Guild relationships:")
                for rel in relationships:
                    print(f"   - {rel.guild_1.name} vs {rel.guild_2.name} ({rel.relationship_type})")
                    print(f"     {rel.description}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating guilds: {e}")

if __name__ == '__main__':
    init_guilds()