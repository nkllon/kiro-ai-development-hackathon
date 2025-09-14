
    def _get_oldest_data_age_hours(self) -> float:
        """Get age of oldest data in hours"""
        oldest_timestamp = None
        for history in self.data_history.values():
            if history:
                first_entry = min(history, key=lambda x: x.timestamp)
                if oldest_timestamp is None or first_entry.timestamp < oldest_timestamp:
                    oldest_timestamp = first_entry.timestamp
        if oldest_timestamp:
            age = datetime.now() - oldest_timestamp
            return age.total_seconds() / 3600
        return 0.0
