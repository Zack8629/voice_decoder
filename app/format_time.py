def format_time(seconds):
    """Форматирует секунды в строку вида 'часы.минуты.секунды'"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f'[{hours}.{minutes:02}.{secs:02}]'
    else:
        return f'[{minutes}.{secs:02}]'
