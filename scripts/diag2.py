for a in dir(seat_sm):
    if 'guide' in a.lower():
        print(repr(a))
raise RuntimeError("methods printed above -> also here: %s"
    % [a for a in dir(seat_sm) if 'guide' in a.lower()])
