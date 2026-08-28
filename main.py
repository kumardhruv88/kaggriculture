def agent(obs):
    """
    Entry point for the Kaggriculture competition agent.
    """
    from utils.state import GameState
    state = GameState(obs)
    
    # Example action, just doing nothing for now.
    return "do_nothing"
