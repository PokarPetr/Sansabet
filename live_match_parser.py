from utils.network import fetch_with_retry
from utils.imports import asyncio, time, ClientError, json, os
from utils.log_config import log_message

list_games = {}

async def parse_one_game(session,  game_key: int,
                         game, urls):
    url = urls.get("parse_one_match").format(0, game['pid'])
    try:
        method = "GET"
        data = await fetch_with_retry(session, url, None, 3, method)

        if not data:
            return

        with open("data.json", 'w') as f:
            f.write(json.dumps(data))

        core_item = data[0]
        h_data = core_item['H']
        if not h_data or 'ParNaziv' not in h_data:
            log_message('warning', f"Missing data in received response. Slid {game['slid']} Pid {game['pid']}")
            return
        home_team, away_team = h_data['ParNaziv'].split(' : ')
        sport = ('Football' if h_data['S'] == 'F' else (
            'Tennis' if h_data['S'] == 'T' else None))

        # Extract the current match time
        current_time = None
        if 'P' in core_item and 'T' in core_item['P']:
            time_data = core_item['P']['T']
            if 'M' in time_data:
                current_time = int(time_data['M'])

        r_data = core_item['R']
        score = "0-0"
        if "G" in r_data:
            score = r_data["G"]

        red_cards = "0-0"
        if "RC" in r_data:
            red_cards = r_data["RC"]

        yellow_cards = "0-0"
        if "YC" in r_data:
            yellow_cards = r_data["YC"]

        one_game = {
            "pid": game['pid'],
            "slid": int(h_data['SLID']),
            "league": h_data['LigaNaziv'],
            "home_team": home_team,
            "away_team": away_team,
            "sport": sport,
            "outcomes": [],
            "current_minute": current_time,
            "time": time.time(),
            "score": score,
            "red_cards": red_cards,
            "yellow_cards": yellow_cards

        }
        # print(one_game, file=open("one_gametut.json", "a"))

        # print(core_item, file=open("core_item.json", "a"))
        if 'M' not in core_item:
            # print("M not in core_item", file=open("M_not_in_core_item.json", "a"))
            return

        koeff_data = core_item['M']
        odds = []

        for koef in koeff_data:
            val_bets = koef['S']
            status = koef['MS']
            if status != "OPEN":
                continue
            for val_bet in val_bets:
                type_bet = int(val_bet['N'])
                odds_value = val_bet['O']

                if sport == 'Football':

                    # Total Goals
                    if type_bet == 103:
                        if not koef.get('B'):
                            continue
                        total_value = float(koef.get('B', '0'))
                        odds.append(
                            {'type_name': 'Total Goals',
                             'type': 'U',
                             'line': total_value,
                             'odds': odds_value})
                    elif type_bet == 105:
                        if not koef.get('B'):
                            continue
                        total_value = float(koef.get('B', '0'))
                        odds.append(
                            {'type_name': 'Total Goals',
                             'type': 'O',
                             'line': total_value,
                             'odds': odds_value})

                    # First Half Total
                    elif type_bet == 165:
                        if not koef.get('B'):
                            continue
                        total_value = float(koef.get('B', '0'))
                        odds.append(
                            {'type_name': 'First Half Total',
                             'type': '1HU',
                             'line': total_value,
                             'odds': odds_value})
                    elif type_bet == 167:
                        if not koef.get('B'):
                            continue
                        total_value = float(koef.get('B', '0'))
                        odds.append(
                            {'type_name': 'First Half Total',
                             'type': '1HO',
                             'line': total_value,
                             'odds': odds_value})

                    # Second Half Total
                    elif type_bet == 754:
                        if koef.get('B') is None:
                            continue
                        total_value = float(koef.get('B', '0'))
                        odds.append(
                            {'type_name': 'Second Half Total',
                             'type': '2HU',
                             'line': total_value,
                             'odds': odds_value})
                    elif type_bet == 755:
                        if koef.get('B') is None:
                            continue
                        total_value = float(koef.get('B', '0'))
                        odds.append(
                            {'type_name': 'Second Half Total',
                             'type': '2HO',
                             'line': total_value,
                             'odds': odds_value})
                # 1X2
                if type_bet == 1:
                    odds.append(
                        {'type_name': '1X2', 'type': '1',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 10:
                    odds.append(
                        {'type_name': '1X2', 'type': '2',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 2:
                    odds.append(
                        {'type_name': '1X2', 'type': 'X',
                         'line': 0,
                         'odds': odds_value})

                # First Half 1X2
                if type_bet == 93:
                    odds.append(
                        {'type_name': 'First Half 1X2',
                         'type': '1H1',
                         'line': 0, 'odds': odds_value})
                elif type_bet == 94:
                    odds.append(
                        {'type_name': 'First Half 1X2',
                         'type': '1H2',
                         'line': 0, 'odds': odds_value})
                elif type_bet == 95:
                    odds.append(
                        {'type_name': 'First Half 1X2',
                         'type': '1HX',
                         'line': 0, 'odds': odds_value})

                # Second Half 1X2
                elif type_bet == 96:
                    odds.append({'type_name': 'Second Half 1X2',
                                 'type': '2H1', 'line': 0,
                                 'odds': odds_value})
                elif type_bet == 97:
                    odds.append({'type_name': 'Second Half 1X2',
                                 'type': '2H2', 'line': 0,
                                 'odds': odds_value})
                elif type_bet == 98:
                    odds.append({'type_name': 'Second Half 1X2',
                                 'type': '2HX', 'line': 0,
                                 'odds': odds_value})



                elif type_bet in [168, 169, 170, 171]:
                    if 'B' not in koef:
                        continue
                    total_value = float(koef['B'])
                    if type_bet in [168, 169]:
                        team = 'H'
                        bet_type = 'TO' if type_bet == 168 else 'TU'
                    else:
                        team = 'A'
                        bet_type = 'TO' if type_bet == 170 else 'TU'
                    odds.append(
                        {'type_name': f'Team {team} Total',
                         'type': team + bet_type,
                         'line': total_value,
                         'odds': odds_value})

                # Set Winner
                if type_bet == 691:
                    odds.append(
                        {'type_name': '1X2', 'type': '1H1',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 692:
                    odds.append(
                        {'type_name': '1X2', 'type': '1H2',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 693:
                    odds.append(
                        {'type_name': '1X2', 'type': '2H1',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 694:
                    odds.append(
                        {'type_name': '1X2', 'type': '2H2',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 695:
                    odds.append(
                        {'type_name': '1X2', 'type': '3H1',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 696:
                    odds.append(
                        {'type_name': '1X2', 'type': '3H2',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 697:
                    odds.append(
                        {'type_name': '1X2', 'type': '4H1',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 698:
                    odds.append(
                        {'type_name': '1X2', 'type': '4H2',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 699:
                    odds.append(
                        {'type_name': '1X2', 'type': '5H1',
                         'line': 0,
                         'odds': odds_value})
                elif type_bet == 700:
                    odds.append(
                        {'type_name': '1X2', 'type': '5H2',
                         'line': 0,
                         'odds': odds_value})

                # Total Games
                elif type_bet == 665:
                    if not koef.get('B'):
                        continue
                    total_value = float(koef.get('B', '0'))
                    odds.append({'type_name': 'Total Games',
                                 'type': 'U',
                                 'line': total_value,
                                 'odds': odds_value})
                elif type_bet == 666:
                    if not koef.get('B'):
                        continue
                    total_value = float(koef.get('B', '0'))
                    odds.append({'type_name': 'Total Games',
                                 'type': 'O',
                                 'line': total_value,
                                 'odds': odds_value})

                # Set Total Games
                for set_num in range(1, 5):
                    if type_bet == 655 + 2 * set_num:
                        if not koef.get('B'):
                            continue
                        total_value = float(
                            koef.get('B', '0'))
                        odds.append({'type_name': 'Total',
                                     'type': f'{set_num}HU',
                                     'line': total_value,
                                     'odds': odds_value})
                    elif type_bet == 656 + 2 * set_num:
                        if not koef.get('B'):
                            continue
                        total_value = float(
                            koef.get('B', '0'))
                        odds.append({'type_name': 'Total',
                                     'type': f'{set_num}HO',
                                     'line': total_value,
                                     'odds': odds_value})

                # Asian Handicap для геймов
                if type_bet == 1193:
                    if not koef.get('B'):
                        continue
                    handicap_value = float(koef.get('B', '0'))
                    odds.append({'type_name': 'Handicap',
                                 'type': 'AH1',
                                 'line': handicap_value,
                                 'odds': odds_value})
                elif type_bet == 1194:
                    if not koef.get('B'):
                        continue
                    handicap_value = float(koef.get('B', '0'))
                    odds.append({'type_name': 'Handicap',
                                 'type': 'AH2',
                                 'line': -handicap_value,
                                 'odds': odds_value})
                elif type_bet == 83:
                    #     1x

                    score1, score2 = score.split("-")
                    score_diff = int(score1) - int(score2)
                    odds.append({'type_name': 'Handicap',
                                 'type': 'AH1',
                                 'line': 0.5 + score_diff,
                                 'odds': odds_value})

                elif type_bet == 85:
                    #             x2
                    score1, score2 = score.split("-")
                    score_diff = int(score2) - int(score1)
                    odds.append({'type_name': 'Handicap',
                                 'type': 'AH2',
                                 'line': 0.5 + score_diff,
                                 'odds': odds_value})
                if type_bet == 746:
                    #     1 тайм индивидуальные тотал 1 команды меньше
                    if not koef.get('B'):
                        continue
                    total_value = float(koef.get('B', '0'))
                    odds.append(
                        {'type_name': '1st Half Team Total',
                         'type': '1HTU',
                         'line': total_value,
                         'odds': odds_value})

                if type_bet == 747:
                    #     1 тайм индивидуальные тотал 1 команды больше
                    if not koef.get('B'):
                        continue
                    total_value = float(koef.get('B', '0'))
                    odds.append(
                        {'type_name': '1st Half Team Total',
                         'type': '1HTO',
                         'line': total_value,
                         'odds': odds_value})

                if type_bet == 748:
                    #     1 тайм индивидуальные тотал 2 команды меньше
                    if not koef.get('B'):
                        continue
                    total_value = float(koef.get('B', '0'))
                    odds.append(
                        {'type_name': '1st Half Team Total',
                         'type': '2HTU',
                         'line': total_value,
                         'odds': odds_value})
                if type_bet == 749:
                    #     1 тайм индивидуальные тотал 2 команды больше
                    if not koef.get('B'):
                        continue
                    total_value = float(koef.get('B', '0'))
                    odds.append(
                        {'type_name': '1st Half Team Total',
                         'type': '2HTO',
                         'line': total_value,
                         'odds': odds_value})
                if type_bet == 121:
                    #             гандикап первой команды
                    if not koef.get('B'):
                        continue
                    score1, score2 = score.split("-")
                    score_diff = int(score1) - int(score2)
                    handicap_value = float(
                        koef.get('B', '0')) - 0.5 + score_diff
                    odds.append(
                        {'type_name': 'Handicap',
                         'type': 'AH1',
                         'line': handicap_value,
                         'odds': odds_value})
                if type_bet == 123:
                    #             гандикап второй команды
                    if not koef.get('B'):
                        continue
                    score1, score2 = score.split("-")
                    score_diff = int(score2) - int(score1)
                    handicap_value = (-float(
                        koef.get('B', '0'))) - 0.5 + score_diff
                    odds.append(
                        {'type_name': 'Handicap',
                         'type': 'AH2',
                         'line': handicap_value,
                         'odds': odds_value})

        one_game['outcomes'] = odds
        one_game['time'] = time.time()

        # logging.debug(json.dumps(one_game, indent=4))

        list_games[game_key] = one_game
        match_name = f"{one_game['home_team']} vs {one_game['away_team']}"
        # проверка на наличие директории
        if not os.path.exists("matches_sansa"):
            os.makedirs("matches_sansa")
        match_name = match_name.replace("/", "")
        print(one_game,
              file=open(f"matches_sansa/{match_name}.json", "a"))

    except (
        ClientError, KeyError, ValueError,
        json.JSONDecodeError) as e:
        log_message("error", f"Error processing game {game['pid']}: {str(e)}")

        list_games.pop(game_key, None)

    return list_games[game_key]