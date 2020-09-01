def get_var(var):
    import mist.sdk.stack as s
    import mist.sdk.mapping as m

    if var in s.stack[len(s.stack)-1]:
        return s.stack[len(s.stack)-1][var]
    if var in m.mapped:
        return m.mapped[var]
    return None
