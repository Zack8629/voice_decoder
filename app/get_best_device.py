import torch


def get_best_device():
    """Определяет наиболее эффективное устройство (GPU или CPU)."""
    try:
        if torch.cuda.is_available():
            return 'cuda'
        elif torch.backends.mps.is_available():  # Apple M1/M2
            return 'mps'
        else:
            if torch.cuda.device_count() > 0:
                print('[WARNING] Whisper работает на CPU, хотя GPU доступен! Возможно, не установлены драйверы.')
                return 'cpu (GPU доступен, но не используется!)'
            return 'cpu'

    except Exception as e:
        print(f'[WARNING] Ошибка при определении устройства: {e}')
        return 'cpu'
