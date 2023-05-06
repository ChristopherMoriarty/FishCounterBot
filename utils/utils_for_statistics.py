from datetime import date, datetime, timedelta
from sqlalchemy import and_, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from models import *

engine = create_engine('sqlite:///fishing.db', echo=True)
Session = sessionmaker(bind=engine)

def fishing_statistics(session, user_id, start_date, end_date):
    
    fishing_trips_query = (session.query(FishingTrip)
                           .filter(and_(FishingTrip.user_id == user_id,
                                        FishingTrip.fishing_date >= start_date,
                                        FishingTrip.fishing_date <= end_date))
                           .all())
    
    catches_count = (session.query(Fish.fishing_date)
                     .filter(and_(Fish.user_id == user_id,
                                  Fish.fishing_date >= start_date,
                                  Fish.fishing_date <= end_date))
                     .distinct()
                     .count())
    
    trips_count = len(fishing_trips_query)
    unsuccessful_trips_count = trips_count - catches_count
    successful_trips_count = trips_count - unsuccessful_trips_count
    
    fish_statistics = {}
    
    for trip in fishing_trips_query:
        fish_query = (session.query(Fish.fish_name, func.sum(Fish.fish_count))
                      .filter(and_(Fish.fishing_date == trip.fishing_date,
                                   Fish.user_id == user_id))
                      .group_by(Fish.fish_name)
                      .all())
        
        for fish in fish_query:
            fish_name, fish_count = fish
            if fish_name in fish_statistics:
                fish_statistics[fish_name] += fish_count
            else:
                fish_statistics[fish_name] = fish_count
    
    total_fish_count = sum([count for count in fish_statistics.values()])
    
    return {'trips_count': trips_count,'successful': successful_trips_count,
            'unsuccessful': unsuccessful_trips_count, 'fish_statistics': fish_statistics,
            'total_fish_count': total_fish_count}


def get_month_range(month_number):
    today = datetime.today()
    start_date = datetime(today.year, month_number, 1).date()
    end_date = datetime(today.year, month_number + 1, 1).date() - timedelta(days=1)
    return (start_date, end_date)

def answers_for_statistics(stats):
    if stats.get('trips_count') == 0:
        return 'За обраний період в тебе не було жодної рибалки 🫡'
    elif not stats.get('fish_statistics'):
        return f'''Твої виїзди на риболовлю: 
Всього рибалок: {stats.get('trips_count')}
Успішних рибалок: {stats.get('successful')}
Не успішних рибалок: {stats.get('unsuccessful')}

За обраний період, нажаль, в тебе немає пійманих трофеїв'''
    else:
        fish_stats_str = '\n'.join([f'{key}: {value}' for key, value in stats['fish_statistics'].items()])
        return f'''Твої виїзди на риболовлю 🛳: 

Всього рибалок: {stats.get('trips_count')} 📊
Успішних рибалок: {stats.get('successful')} ✅
Не успішних рибалок: {stats.get('unsuccessful')} ❌

Твої трофеї 🎣: 

{fish_stats_str}

Загальна кількість риб: {stats.get('total_fish_count')} 😎'''