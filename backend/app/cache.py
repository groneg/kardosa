import redis
import json
import logging
from typing import Any, Optional
from . import db
from .models import Player, Team, CardSet

class PersistentCache:
    def __init__(self, redis_url='redis://localhost:6379/0'):
        """
        Initialize Redis connection for persistent caching
        
        Args:
            redis_url (str): Redis connection URL
        """
        self.redis = None
        try:
            self.redis = redis.Redis.from_url(redis_url)
            # Test connection
            self.redis.ping()
            logging.info("Redis connection established successfully")
        except Exception as e:
            logging.warning(f"Could not connect to Redis: {e}")
            logging.warning("Falling back to in-memory caching")
            self.redis = None
        
        # In-memory fallback cache
        self._players_cache = {}
        self._teams_cache = {}
        self._card_sets_cache = {}
    
    def _store_in_memory(self, cache_type, data):
        """Store data in in-memory cache when Redis is unavailable"""
        if cache_type == 'players':
            self._players_cache = data
        elif cache_type == 'teams':
            self._teams_cache = data
        elif cache_type == 'card_sets':
            self._card_sets_cache = data
    
    def _get_from_memory(self, cache_type):
        """Retrieve data from in-memory cache"""
        if cache_type == 'players':
            return self._players_cache
        elif cache_type == 'teams':
            return self._teams_cache
        elif cache_type == 'card_sets':
            return self._card_sets_cache
        return None

    def cache_players(self):
        """
        Cache all players with their full details
        Stores as a JSON-serialized dictionary
        """
        players = Player.query.all()
        players_dict = {
            player.id: {
                'full_name': player.full_name,
                'first_name': getattr(player, 'first_name', ''),
                'last_name': getattr(player, 'last_name', ''),
            } for player in players
        }
        
        if self.redis:
            try:
                self.redis.setex('players_cache', 86400, json.dumps(players_dict))
            except Exception as e:
                logging.warning(f"Redis caching failed for players: {e}")
        
        # Always store in memory as fallback
        self._store_in_memory('players', players_dict)
        
        logging.info(f"Cached {len(players_dict)} players")
        return players_dict
    
    def cache_teams(self):
        """
        Cache all teams with their details
        """
        teams = Team.query.all()
        teams_dict = {
            team.id: {
                'name': team.name,
                'abbreviation': team.abbreviation,
                # Add other relevant fields
            } for team in teams
        }
        
        if self.redis:
            try:
                self.redis.setex('teams_cache', 86400, json.dumps(teams_dict))
            except Exception as e:
                logging.warning(f"Redis caching failed for teams: {e}")
        
        # Always store in memory as fallback
        self._store_in_memory('teams', teams_dict)
        
        logging.info(f"Cached {len(teams_dict)} teams")
        return teams_dict
    
    def cache_card_sets(self):
        """
        Cache card sets with their details
        """
        card_sets = CardSet.query.all()
        card_sets_dict = {
            card_set.id: {
                'name': card_set.name,
                'year': card_set.year,
                # Add other relevant fields
            } for card_set in card_sets
        }
        
        if self.redis:
            try:
                self.redis.setex('card_sets_cache', 86400, json.dumps(card_sets_dict))
            except Exception as e:
                logging.warning(f"Redis caching failed for card sets: {e}")
        
        # Always store in memory as fallback
        self._store_in_memory('card_sets', card_sets_dict)
        
        logging.info(f"Cached {len(card_sets_dict)} card sets")
        return card_sets_dict
    
    def get_cached_players(self) -> Optional[dict]:
        """
        Retrieve cached players
        
        Returns:
            dict: Cached players or None if not found
        """
        if self.redis:
            try:
                cached_players = self.redis.get('players_cache')
                if cached_players:
                    return json.loads(cached_players)
            except Exception as e:
                logging.warning(f"Redis retrieval failed for players: {e}")
        
        # Fallback to in-memory cache
        return self._get_from_memory('players')
    
    def get_cached_teams(self) -> Optional[dict]:
        """
        Retrieve cached teams
        
        Returns:
            dict: Cached teams or None if not found
        """
        if self.redis:
            try:
                cached_teams = self.redis.get('teams_cache')
                if cached_teams:
                    return json.loads(cached_teams)
            except Exception as e:
                logging.warning(f"Redis retrieval failed for teams: {e}")
        
        # Fallback to in-memory cache
        return self._get_from_memory('teams')
    
    def get_cached_card_sets(self) -> Optional[dict]:
        """
        Retrieve cached card sets
        
        Returns:
            dict: Cached card sets or None if not found
        """
        if self.redis:
            try:
                cached_card_sets = self.redis.get('card_sets_cache')
                if cached_card_sets:
                    return json.loads(cached_card_sets)
            except Exception as e:
                logging.warning(f"Redis retrieval failed for card sets: {e}")
        
        # Fallback to in-memory cache
        return self._get_from_memory('card_sets')
    
    def cache_all(self):
        """
        Cache all reference data
        """
        self.cache_players()
        self.cache_teams()
        self.cache_card_sets()

# Create a global cache instance
persistent_cache = PersistentCache() 