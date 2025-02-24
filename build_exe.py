import os
import time

from app import APP_VERSION

try:
    name_exe = f'voice_decoder_{APP_VERSION}'
    whisper_assets = os.path.normpath('.venv/Lib/site-packages/whisper/assets')

    # Команда для PyInstaller
    command = (
        # f'pyinstaller --noconsole '
        f'pyinstaller '
        f'--icon=app/main.ico '
        f'--name="{name_exe}" '
        f'--add-data "app/main.ico;app/" '
        f'--add-data "ffmpeg;ffmpeg" '
        f'--add-data "whisper_models;whisper_models" '
        f'--add-data "{whisper_assets};whisper/assets" '
        'run.py'
    )


except Exception as e:
    print(f'Error name_exe and command => {e}')
    raise 'Error command or paths'


def del_spec_file(name_spec_file):
    try:
        name_spec_file = f'{name_spec_file}.spec'
        if os.path.exists(name_spec_file):
            os.remove(name_spec_file)

    except Exception as e:
        print(f'Error del_spec_file => {e}')


if __name__ == '__main__':
    try:
        os.system(command)

        time.sleep(1)
        del_spec_file(name_exe)

        print('Build exe file done!')

    except Exception as e:
        print(f'Error main => {e}')
