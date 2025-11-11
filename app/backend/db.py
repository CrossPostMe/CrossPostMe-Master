# Supabase-only stub for legacy get_db usage
class SupabaseDB:
    def __init__(self):
        pass

    # Add any methods needed for compatibility


def get_db() -> SupabaseDB:
    return SupabaseDB()

# Minimal compatibility layer for code expecting a typed DB interface
# Keeps behavior identical by delegating to get_db()

def get_typed_db() -> SupabaseDB:  # type: ignore[override]
    return get_db()
