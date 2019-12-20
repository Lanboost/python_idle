def run_action_once(obj):
    obj["action"].__next__()
    