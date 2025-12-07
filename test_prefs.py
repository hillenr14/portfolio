from src.data.store import DataStore

def test_preferences():
    print("Testing User Preferences Persistence...")
    store = DataStore()
    
    # Test Set
    key = "test_key"
    val = "test_value"
    store.set_preference(key, val)
    print(f"Set {key} = {val}")
    
    # Test Get
    retrieved = store.get_preference(key)
    print(f"Retrieved {key} = {retrieved}")
    
    assert retrieved == val
    
    # Test Overwrite
    new_val = "new_value"
    store.set_preference(key, new_val)
    retrieved_new = store.get_preference(key)
    print(f"Overwrote {key} = {retrieved_new}")
    
    assert retrieved_new == new_val
    
    print("Preferences Test Passed!")

if __name__ == "__main__":
    test_preferences()
