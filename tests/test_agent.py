import os
import sys
import time
import json
from datetime import datetime

# Ensure we can import from the main project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from kaggle_environments import make
except ImportError:
    print("Please install kaggle_environments: pip install kaggle-environments")
    sys.exit(1)

from main import agent

def run_quick_test():
    print("--- Running Quick Test (72 steps) vs Random ---")
    env = make("kaggriculture", configuration={"episodeSteps": 72}, debug=True)
    
    try:
        env.run([agent, "random"])
        final = env.steps[-1]
        
        our_score = final[0].reward if final[0].reward is not None else 0
        rand_score = final[1].reward if final[1].reward is not None else 0
        
        print(f"\nOur Agent Score:    ${our_score:.0f}")
        print(f"Random Agent Score: ${rand_score:.0f}")
        
        if our_score > rand_score:
            print("Result: WIN 🎉")
        elif our_score < rand_score:
            print("Result: LOSE 😢")
        else:
            print("Result: TIE 🤝")
            
        print(f"Turns completed: {len(env.steps)}")
    except Exception as e:
        print(f"Error caught during simulation: {e}")


def run_full_season():
    print("--- Running Full Season (720 steps) vs Random ---")
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    
    env.run([agent, "random"])
    final = env.steps[-1]
    
    our_score = final[0].reward if final[0].reward is not None else 0
    rand_score = final[1].reward if final[1].reward is not None else 0
    
    print(f"\nFinal Score - Our Agent: ${our_score:.0f}")
    print(f"Final Score - Random:    ${rand_score:.0f}")
    
    if our_score > rand_score:
        print(f"Winner: OUR AGENT (Margin: ${our_score - rand_score:.0f})")
    elif our_score < rand_score:
        print(f"Winner: RANDOM AGENT (Margin: ${rand_score - our_score:.0f})")
    else:
        print("Winner: TIE")
        
    print("\nScore Breakdown Estimate:")
    print("- Detail tracker requires environment event logs.")
    print("- Currently showing net raw score from env variables.")
    
    # Save replay
    os.makedirs("replays", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"replays/replay_{timestamp}.json"
    
    with open(filepath, "w") as f:
        json.dump(env.toJSON(), f)
    print(f"\nReplay saved to: {filepath}")


def run_self_play(n=5):
    print(f"--- Running Self-Play ({n} games) ---")
    scores = []
    
    for i in range(n):
        print(f"Starting Game {i+1}...")
        env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
        env.run([agent, agent])
        final = env.steps[-1]
        
        s1 = final[0].reward if final[0].reward is not None else 0
        s2 = final[1].reward if final[1].reward is not None else 0
        
        # In self-play, track the average across both agents
        scores.extend([s1, s2])
        print(f"  Game {i+1} Results: P1=${s1:.0f} | P2=${s2:.0f}")
        
    avg_score = sum(scores) / len(scores)
    variance = sum((x - avg_score) ** 2 for x in scores) / len(scores)
    
    print("\nSelf-Play Stats:")
    print(f"Average Score: ${avg_score:.2f}")
    print(f"Score Variance: {variance:.2f}")


def run_vs_starter():
    print("--- Running Full Season vs Starter Agent ---")
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
        env.run([agent, "starter"])  # Fails back to random if "starter" doesn't exist
        final = env.steps[-1]
        
        our_score = final[0].reward if final[0].reward is not None else 0
        starter_score = final[1].reward if final[1].reward is not None else 0
        
        print(f"\nOur Agent Score:    ${our_score:.0f}")
        print(f"Starter Agent Score: ${starter_score:.0f}")
        
        if our_score > starter_score:
            print("Result: WIN 🎉")
        elif our_score < starter_score:
            print("Result: LOSE 😢")
        else:
            print("Result: TIE 🤝")
    except Exception as e:
        print(f"Error running against starter (may not exist natively in env): {e}")


def benchmark_speed():
    print("--- Benchmarking Agent Speed ---")
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    
    # We step manually to accurately time our agent logic
    trainer = env.train([None, "random"])
    obs = trainer.reset()
    
    times = []
    
    while not env.done:
        start_t = time.time()
        action = agent(obs)
        end_t = time.time()
        
        dur_ms = (end_t - start_t) * 1000
        times.append(dur_ms)
        
        obs, reward, done, info = trainer.step(action)
        
    avg_ms = sum(times) / len(times)
    max_ms = max(times)
    
    print(f"\nAverage time per turn: {avg_ms:.2f} ms")
    print(f"Max time per turn:     {max_ms:.2f} ms")
    
    if avg_ms > 50:
        print("\n⚠️ WARNING: Average time exceeds 50ms (submission timeout risk)!")
    else:
        print("\n✅ Speed is well within safety margins.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "quick"
    
    if mode == "quick":
        run_quick_test()
    elif mode == "full":
        run_full_season()
    elif mode == "self":
        run_self_play()
    elif mode == "starter":
        run_vs_starter()
    elif mode == "bench":
        benchmark_speed()
    else:
        print(f"Unknown mode '{mode}'. Available modes: quick, full, self, starter, bench")
