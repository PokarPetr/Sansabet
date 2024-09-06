
from utils.imports import asyncio, time, datetime, random, os
from utils.network import fetch_with_retry


parsed_matches = {}

async def parse_one_match(session, match, url, semaphore):
    await asyncio.sleep(random.uniform(0.01, 1))
    async with semaphore:
        data = {
            "PairId": match['match_id'],

        }
        try:
            odds_data = await fetch_with_retry(session, url, data) #URL4
        except Exception as e:
            odds_data = await fetch_with_retry(session, url, data)
        if not isinstance(odds_data, list):  # handle error
            return None

        parsed_odds = []

        for odds_type in odds_data:
            try:
                # 1X2
                if odds_type['ID'] == 1:
                    for odd in odds_type['T']:
                        parsed_odds.append({
                            "type_name": "1X2",
                            "type": odd['TipPecatiWeb'],
                            "line": 0.0,
                            "odds": odd['Kvota'],
                            "single": odd["Single"]
                        })

                # 1 half 1X2
                elif odds_type['ID'] == 7:
                    for odd in odds_type['T']:
                        parsed_odds.append({
                            "type_name": "1 half 1X2",
                            "type": '1H' + odd['TipPecatiWeb'][0],
                            "line": 0.0,
                            "odds": odd['Kvota'],
                            "single": odd["Single"]
                        })

                # 2 half 1X2
                elif odds_type['ID'] == 8:
                    for odd in odds_type['T']:
                        parsed_odds.append({
                            "type_name": "2 half 1X2",
                            "type": '2H' + odd['TipPecatiWeb'][0],
                            "line": 0.0,
                            "odds": odd['Kvota'],
                            "single": odd["Single"]
                        })

                # Totals
                elif odds_type['ID'] == 14:
                    for odd in odds_type['T']:
                        total_type = ('U' if '-' in odd['TipPecatiWeb'] else 'O')
                        parsed_odds.append({
                            "type_name": "Totals",
                            "type": total_type,
                            "line": (int(odd[
                                             'TipVnes']) + 0.5 if total_type == 'U' else int(
                                odd['TipVnes']) - 0.5),
                            "odds": odd['Kvota'],
                            "single": odd["Single"]
                        })
                # 1 half Totals over
                elif odds_type['ID'] == 17:
                    for odd in odds_type['T']:
                        if '.' in odd['TipVnes'] or '*' in odd['TipVnes']:
                            splited = odd['TipPecatiWeb'].split()
                            if splited[0] == "0":
                                parsed_odds.append({
                                    "type_name": "1 half Totals",
                                    "type": '1H' + 'U',
                                    "line": 0.5,
                                    "odds": odd['Kvota'],
                                    "single": odd["Single"]
                                })
                            continue
                        if "+" in odd['TipPecatiWeb']:
                            goal = odd['TipPecatiWeb'].split("+")
                            if len(goal) > 1:
                                parsed_odds.append({
                                    "type_name": "1 half Totals",
                                    "type": '1H' + 'O',
                                    "line": (int(goal[0]) - 0.5),
                                    "odds": odd['Kvota'],
                                    "single": odd["Single"]
                                })



                # 1 half Totals under
                elif odds_type['ID'] == 18:
                    for odd in odds_type['T']:
                        if '.' in odd['TipVnes'] or '*' in odd['TipVnes']:
                            continue
                        gools = odd['TipPecatiWeb'].split()
                        if len(gools) > 0:
                            gools = gools[0]
                            if "-" in gools:
                                gools = gools.split('-')
                                if len(gools) > 1:
                                    goal1, goal2 = gools
                                    if goal1 == "0":
                                        parsed_odds.append({
                                            "type_name": "1 half Totals",
                                            "type": '1H' + 'U',
                                            "line": float(goal2) + 0.5,
                                            "odds": odd['Kvota'],
                                            "single": odd["Single"]
                                        })
                # 2 half Totals over
                elif odds_type['ID'] == 20:
                    for odd in odds_type['T']:
                        if '.' in odd['TipVnes'] or '*' in odd['TipVnes']:
                            splited = odd['TipPecatiWeb'].split()
                            if splited[0] == "0":
                                parsed_odds.append({
                                    "type_name": "2 half Totals",
                                    "type": '2H' + 'U',
                                    "line": 0.5,
                                    "odds": odd['Kvota'],
                                    "single": odd["Single"]
                                })
                            continue
                        if "+" in odd['TipPecatiWeb']:
                            goal = odd['TipPecatiWeb'].split("+")
                            if len(goal) > 1:
                                parsed_odds.append({
                                    "type_name": "2 half Totals",
                                    "type": '2H' + 'O',
                                    "line": (int(goal[0]) - 0.5),
                                    "odds": odd['Kvota'],
                                    "single": odd["Single"]
                                })



                # 2 half Totals under
                elif odds_type['ID'] == 21:
                    for odd in odds_type['T']:
                        if '.' in odd['TipVnes'] or '*' in odd['TipVnes']:
                            continue
                        gools = odd['TipPecatiWeb'].split()
                        if len(gools) > 0:
                            gools = gools[0]
                            if "-" in gools:
                                gools = gools.split('-')
                                if len(gools) > 1:
                                    goal1, goal2 = gools
                                    if goal1 == "0":
                                        parsed_odds.append({
                                            "type_name": "2 half Totals",
                                            "type": '2H' + 'U',
                                            "line": float(goal2) + 0.5,
                                            "odds": odd['Kvota'],
                                            "single": odd["Single"]
                                        })

                # 1 half Totals
                # elif odds_type['ID'] == 17:
                #     for odd in odds_type['T']:
                #         if '.' in odd['TipVnes'] or '*' in odd['TipVnes']:
                #             continue
                #
                #         total_type = ('U' if '-' in odd['TipPecatiWeb'] else 'O')
                #         parsed_odds.append({
                #             "type_name": "1 half Totals",
                #             "type": '1H' + total_type,
                #             "line": (int(odd['TipVnes'][
                #                              -1]) + 0.5 if total_type == 'U' else int(
                #                 odd['TipVnes'][-1]) - 0.5),
                #             "odds": odd['Kvota'],
                #             "single": odd["Single"]
                #         })
                #
                # # 2 half Totals
                # elif odds_type['ID'] == 20:
                #     for odd in odds_type['T']:
                #         if '.' in odd['TipVnes'] or '*' in odd['TipVnes']:
                #             continue
                #
                #         total_type = ('U' if '-' in odd['TipPecatiWeb'] else 'O')
                #         parsed_odds.append({
                #             "type_name": "1 half Totals",
                #             "type": '2H' + total_type,
                #             "line": (int(odd['TipVnes'][
                #                              -1]) + 0.5 if total_type == 'U' else int(
                #                 odd['TipVnes'][-1]) - 0.5),
                #             "odds": odd['Kvota'],
                #             "single": odd["Single"]
                #         })

                # Team 1 Totals
                elif odds_type['ID'] == 27:
                    for odd in odds_type['T']:
                        if ('.' in odd['TipVnes'] or odd['TipPecatiWeb'][-2] in [
                            '=', '>', '<']):
                            continue

                        if odd['TipPecatiWeb'].endswith('0'):
                            parsed_odds.append({
                                "type_name": "Team 1 Totals",
                                "type": "HTU",
                                "line": 0.5,
                                "odds": odd['Kvota'],
                                "unparsed": odd['TipPecati'],
                                "single": odd["Single"]
                            })
                            continue

                        total_type = ('O' if '+' in odd['TipPecatiWeb'] else 'O')
                        parsed_odds.append({
                            "type_name": "Team 1 Totals",
                            "type": "HT" + total_type,
                            "line": (int(odd['TipPecatiWeb'][
                                             -2]) - 0.5 if total_type == 'O' else 0.0),
                            "odds": odd['Kvota'],
                            "unparsed": odd['TipPecati'],
                            "single": odd["Single"]
                        })

                # Team 2 Totals
                elif odds_type['ID'] == 32:
                    for odd in odds_type['T']:
                        if ('.' in odd['TipVnes'] or odd['TipPecatiWeb'][-2] in [
                            '=', '>', '<']):
                            continue

                        if odd['TipPecatiWeb'].endswith('0'):
                            parsed_odds.append({
                                "type_name": "Team 2 Totals",
                                "type": "ATU",
                                "line": 0.5,
                                "odds": odd['Kvota'],
                                "unparsed": odd['TipPecati'],
                                "single": odd["Single"]
                            })
                            continue

                        total_type = ('O' if '+' in odd['TipPecatiWeb'] else 'O')
                        parsed_odds.append({
                            "type_name": "Team 2 Totals",
                            "type": "AT" + total_type,
                            "line": (int(odd['TipPecatiWeb'][
                                             -2]) - 0.5 if total_type == 'O' else 0.0),
                            "odds": odd['Kvota'],
                            "unparsed": odd['TipPecati'],
                            "single": odd["Single"]
                        })

                # Team 1 Totals Scope
                elif odds_type['ID'] == 28:
                    for odd in odds_type['T']:
                        if '0-' not in odd['TipPecati']:
                            continue

                        parsed_odds.append({
                            "type_name": "Team 1 Totals",
                            "type": "HTU",
                            "line": float(odd['TipPecatiWeb'][-1] + '.5'),
                            "odds": odd['Kvota'],
                            "unparsed": odd['TipPecati'],
                            "single": odd["Single"]
                        })

                # Team 2 Totals Scope
                elif odds_type['ID'] == 33:
                    for odd in odds_type['T']:
                        if '0-' not in odd['TipPecati']:
                            continue

                        parsed_odds.append({
                            "type_name": "Team 2 Totals",
                            "type": "ATU",
                            "line": float(odd['TipPecatiWeb'][-1] + '.5'),
                            "odds": odd['Kvota'],
                            "unparsed": odd['TipPecati'],
                            "single": odd["Single"]
                        })

                # Team 1 Totals 1st half
                elif odds_type['ID'] == 29:
                    for odd in odds_type['T']:
                        odd_line = odd['TipPecati'].split()[1]
                        if odd_line != '0' and '+' not in odd_line:
                            if odd_line == "0-1":
                                parsed_odds.append({
                                    "type_name": "1st half Team 1 Totals",
                                    "type": "1HHTU",
                                    "line": 1.5,
                                    "odds": odd['Kvota'],
                                    "unparsed": odd['TipPecati'],
                                    "single": odd["Single"]
                                })

                            continue

                        parsed_odds.append({
                            "type_name": "1st half Team 1 Totals",
                            "type": "1HHT" + ('U' if odd_line == '0' else 'O'),
                            "line": (0.5 if odd_line == '0' else int(
                                odd_line.replace('+', '')) - 0.5),
                            "odds": odd['Kvota'],
                            "unparsed": odd['TipPecati'],
                            "single": odd["Single"]
                        })

                # Team 1 Totals 2nd half
                elif odds_type['ID'] == 30:
                    for odd in odds_type['T']:
                        odd_line = odd['TipPecati'].split()[1]
                        if odd_line != '0' and '+' not in odd_line:
                            if odd_line == "0-1":
                                parsed_odds.append({
                                    "type_name": "2nd half Team 1 Totals",
                                    "type": "2HHTU",
                                    "line": 1.5,
                                    "odds": odd['Kvota'],
                                    "unparsed": odd['TipPecati'],
                                    "single": odd["Single"]
                                })
                            continue

                        parsed_odds.append({
                            "type_name": "2nd half Team 1 Totals",
                            "type": "2HHT" + ('U' if odd_line == '0' else 'O'),
                            "line": (0.5 if odd_line == '0' else int(
                                odd_line.replace('+', '')) - 0.5),
                            "odds": odd['Kvota'],
                            "unparsed": odd['TipPecati'],
                            "single": odd["Single"]
                        })

                # Team 2 Totals 1st half
                elif odds_type['ID'] == 34:
                    for odd in odds_type['T']:
                        odd_line = odd['TipPecati'].split()[1]
                        if odd_line != '0' and '+' not in odd_line:
                            if odd_line == "0-1":
                                parsed_odds.append({
                                    "type_name": "1st half Team 2 Totals",
                                    "type": "1HATU",
                                    "line": 1.5,
                                    "odds": odd['Kvota'],
                                    "unparsed": odd['TipPecati'],
                                    "single": odd["Single"]
                                })
                            continue

                        parsed_odds.append({
                            "type_name": "1st half Team 2 Totals",
                            "type": "1HAT" + ('U' if odd_line == '0' else 'O'),
                            "line": (0.5 if odd_line == '0' else int(
                                odd_line.replace('+', '')) - 0.5),
                            "odds": odd['Kvota'],
                            "unparsed": odd['TipPecati'],
                            "single": odd["Single"]
                        })

                # Team 2 Totals 2nd half
                elif odds_type['ID'] == 35:
                    for odd in odds_type['T']:
                        odd_line = odd['TipPecati'].split()[1]

                        if odd_line != '0' and '+' not in odd_line:

                            if odd_line == "0-1":
                                parsed_odds.append({
                                    "type_name": "2nd half Team 2 Totals",
                                    "type": "2HATU",
                                    "line": 1.5,
                                    "odds": odd['Kvota'],
                                    "unparsed": odd['TipPecati'],
                                    "single": odd["Single"]
                                })
                            continue

                        parsed_odds.append({
                            "type_name": "2nd half Team 2 Totals",
                            "type": "2HAT" + ('U' if odd_line == '0' else 'O'),
                            "line": (0.5 if odd_line == '0' else int(
                                odd_line.replace('+', '')) - 0.5),
                            "odds": odd['Kvota'],
                            "unparsed": odd['TipPecati'],
                            "single": odd["Single"]
                        })

                # Handicaps
                elif odds_type['ID'] == 42:
                    for odd in odds_type['T']:
                        hcp = odd['TipPecatiWeb'].split()
                        if hcp[1] == 'X':
                            continue

                        if hcp[1] == '1':
                            parsed_odds.append({
                                "type_name": "Asian Handicap",
                                "type": f"AH{hcp[1]}",
                                "line": float(hcp[2]) - 0.5,
                                "odds": odd['Kvota'],
                                "single": odd["Single"]
                            })

                        elif hcp[1] == '2':
                            parsed_odds.append({
                                "type_name": "Asian Handicap",
                                "type": f"AH{hcp[1]}",
                                "line": -(float(hcp[2])) - 0.5,
                                "odds": odd['Kvota'],
                                "single": odd["Single"]
                            })
                # Game Handicap (Hendikep Gemova)
                elif odds_type['ID'] == 235:
                    for odd in odds_type['T']:
                        hcp = odd['TipPecatiWeb'].split()
                        if hcp[1] == 'X':
                            continue

                        if hcp[1] == '1':
                            parsed_odds.append({
                                "type_name": "games Asian Handicap",
                                "type": f"GAH{hcp[1]}",
                                "line": float(hcp[2]) - 0.5,
                                "odds": odd['Kvota'],
                                "single": odd["Single"]
                            })

                        elif hcp[1] == '2':
                            parsed_odds.append({
                                "type_name": "games Asian Handicap",
                                "type": f"GAH{hcp[1]}",
                                "line": -(float(hcp[2])) - 0.5,
                                "odds": odd['Kvota'],
                                "single": odd["Single"]
                            })

                # Total Games (Ukupno Gemova)
                elif odds_type['ID'] == 64:
                    for odd in odds_type['T']:
                        total_type = 'U' if odd['TipVnes'] == "-" else 'O'
                        parsed_odds.append({
                            "type_name": "Total Games",
                            "type": total_type,
                            "line": float(odd['G']),
                            "odds": odd['Kvota'],
                            "single": odd["Single"]
                        })

                # First Set Winner (Pobednik - Prvi Set)
                elif odds_type['ID'] == 68:
                    for odd in odds_type['T']:
                        parsed_odds.append({
                            "type_name": "First Set Winner",
                            "type": "1H1" if odd['TipVnes'] == "11" else "1H2",
                            "line": 0.0,
                            "odds": odd['Kvota'],
                            "single": odd["Single"]
                        })

                # First Set Total Games (Ukupno Poena - Prvi Set)
                elif odds_type['ID'] == 172:
                    for odd in odds_type['T']:
                        total_type = 'U' if odd['TipVnes'].endswith('-') else 'O'
                        parsed_odds.append({
                            "type_name": "First Set Total Games",
                            "type": f"1H{total_type}",
                            "line": float(odd['G']),
                            "odds": odd['Kvota'],
                            "single": odd["Single"]
                        })
            except Exception as e:
                print(f"Error occurred while parsing odds: {e}")
                print(f"Error occurred while parsing odds: {e}",
                      datetime.now(), file=open('log_sansa.txt', 'a'))
                continue

        match['outcomes'] = parsed_odds
        match['time'] = datetime.now().timestamp()
        print(
            f"Match {match['home_team']} vs {match['away_team']} parsed {datetime.now()}",
            file=open('log_sansa_.txt', 'a'))
        parsed_matches[match['match_id']] = match
        # проверяем что папка существует
        # сохраняем в файл
        if not os.path.exists('parsed_sansa_matches'):
            os.makedirs('parsed_sansa_matches')
        match_name = match['home_team'] + ' vs ' + match['away_team']
        safety_match_name = match_name.replace('/', ' ')
        match["time"] = datetime.now().timestamp()
        with open(f"parsed_sansa_matches/{safety_match_name}.json",
                  "a") as f:
            print(match, file=f)
        return match['match_id']
