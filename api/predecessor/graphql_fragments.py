"""Shared GraphQL fragments for Predecessor API queries."""

# Shared fragment for matchPlayers fields - used by both MatchService and PlayerMatchesService
MATCH_PLAYERS_FRAGMENT = """
    matchPlayers {
        player {
            uuid
            name
        }
        hero {
            name
        }
        heroData {
            name
            displayName
            icon
        }
        team
        role
        kills
        deaths
        assists
        minionsKilled
        gold
        rating {
            points
            newPoints
        }
    }
"""
