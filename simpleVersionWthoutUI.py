import requests

battle_tags = ['enexety-2898', 'POPA-21120', 'ewwum-1746', 'Wowa-2430', 'Yata-21885', 'DeadByDream-1452',
              'Dublicator-21961', 'Quaad-2833', 'perforator-21112', 'Decapitator-21351', 'TTTTTTTTTTTT-21533',
              'DVA-22340', 'Exelero-21842', 'DeadByDream-21116', 'Demotivator-21649', 'Whistle-2386',
              'hotsmurfette-2819', 'koteika-21475']

for unit in battle_tags:
    print('---------------------------------------------')
    print(f'Username: {unit.split("-")[0]}')
    response = requests.get(f'https://overfast-api.tekrop.fr/players/{unit}').json()
    try:
        profile_privacy = str(response['summary']['privacy']).capitalize()
        print(f'Profile: {profile_privacy}')

        if profile_privacy == 'Public':
            endorsement_level = response['summary']['endorsement']['level']
            print(f'Endorsement level: {endorsement_level}\n')

            if type(response['summary']['competitive']) is dict:
                print('Competitive, ', end='')

                try:  # competitive

                    season = response['summary']['competitive']['pc']['season']

                    # stats
                    stats = response['stats']['pc']['competitive']['career_stats']['all-heroes']
                    eliminations = next(
                        stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'eliminations')
                    deaths = next(stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'deaths')

                    sec_played = next(
                        stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if
                        stat['key'] == 'time_played')
                    games_played = next(
                        stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if
                        stat['key'] == 'games_played')
                    games_won = next(
                        stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if
                        stat['key'] == 'games_won')

                    time_played = f'{sec_played // 3600} hours {(sec_played % 3600) // 60} minutes'
                    win_rate = f"{(games_won / games_played) * 100:.2f}%"
                    kd = f'{eliminations / deaths:.2f}'
                    print(f"season {season}: ")
                    print(f'Time played: {time_played}')
                    print(f'Win rate: {win_rate}')
                    print(f'KD: {kd}', end='\n\n')

                    # rating
                    if type(response['summary']['competitive']['pc']['tank']) is dict:
                        tank_division = str(response['summary']['competitive']['pc']['tank']['division']).capitalize()
                        tank_division_tier = str(response['summary']['competitive']['pc']['tank']['tier'])
                        tank_rating = tank_division + '-' + tank_division_tier
                        print(f'Tank: {tank_rating}')
                    else:
                        tank_rating = None

                    if type(response['summary']['competitive']['pc']['damage']) is dict:
                        damage_division = str(
                            response['summary']['competitive']['pc']['damage']['division']).capitalize()
                        damage_division_tier = str(response['summary']['competitive']['pc']['damage']['tier'])
                        damage_rating = damage_division + '-' + damage_division_tier
                        print(f'Damage: {damage_rating}')
                    else:
                        damage_rating = None

                    if type(response['summary']['competitive']['pc']['support']) is dict:
                        support_division = str(
                            response['summary']['competitive']['pc']['support']['division']).capitalize()
                        support_division_tier = str(response['summary']['competitive']['pc']['support']['tier'])
                        support_rating = support_division + '-' + support_division_tier
                        print(f'Support: {support_rating}')
                    else:
                        support_rating = None

                except Exception as e:  # Possibly could happen if no 'pc' stats
                    print(f'Error: something went wrong({e})')

            else:  # for quick stats

                # stats
                stats = response['stats']['pc']['quickplay']['career_stats']['all-heroes']
                eliminations = next(
                    stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'eliminations')
                deaths = next(stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'deaths')

                sec_played = next(
                    stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if
                    stat['key'] == 'time_played')
                games_played = next(
                    stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if
                    stat['key'] == 'games_played')
                games_won = next(
                    stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if
                    stat['key'] == 'games_won')

                time_played = f'{sec_played // 3600} hours {(sec_played % 3600) // 60} minutes'
                win_rate = f"{(games_won / games_played) * 100:.2f}%"
                kd = f'{eliminations / deaths:.2f}'
                print('Quick play:')
                print(f'Time played: {time_played}')
                print(f'Win rate: {win_rate}')
                print(f'KD: {kd}')

        else:  # Profile is closed
            print('Information hidden.')

    except KeyError:  # It happens when couldn't get blizzard page
        print(f'Error: {response["error"]}.')
