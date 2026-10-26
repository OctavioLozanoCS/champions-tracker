import argparse
import sys
import json
from db import init_db, add_match, get_matches, get_stats

def main():
    init_db()
    parser = argparse.ArgumentParser(description="Record a Pokemon Champions match")
    parser.add_argument("--result", "-r", required=True, choices=["WIN", "LOSS", "DRAW", "win", "loss", "draw"], help="Result of the match")
    parser.add_argument("--my-team", "-m", required=True, help="Your team (comma-separated Pokemon names, e.g. 'Miraidon, Incineroar, Whimsicott')")
    parser.add_argument("--opp-team", "-o", required=True, help="Opponent team (comma-separated Pokemon names, e.g. 'Koraidon, Flutter Mane, Urshifu')")
    parser.add_argument("--format", "-f", default="Ranked Doubles", choices=["Ranked Doubles", "Ranked Singles", "Casual", "Private"], help="Battle format")
    parser.add_argument("--tier", "-t", default="", help="Rank / Tier (e.g. Master Ball, Ultra Ball)")
    parser.add_argument("--opponent", "-p", default="", help="Opponent trainer name")
    parser.add_argument("--score", "-s", default="", help="Score/remaining Pokemon, e.g. '4-0', '2-0'")
    parser.add_argument("--mvp", default="", help="MVP Pokemon of the match")
    parser.add_argument("--notes", "-n", default="", help="Notes / observations / misplays / key items")
    parser.add_argument("--source", default="manual", help="Source: manual or screenshot")

    args = parser.parse_args()

    match_id = add_match(
        result=args.result.upper(),
        my_team=args.my_team,
        opp_team=args.opp_team,
        format=args.format,
        tier=args.tier,
        opponent_name=args.opponent,
        score=args.score,
        notes=args.notes,
        mvp=args.mvp,
        source=args.source
    )

    stats = get_stats()
    print(f"Match #{match_id} recorded successfully! ({args.result.upper()})")
    print(f"Overall Record: {stats['wins']}W - {stats['losses']}L ({stats['win_rate']}%) | Current Streak: {stats['streak']}")

if __name__ == "__main__":
    main()
