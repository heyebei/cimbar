"""
Simple GUI for cimbar encode/decode using PySimpleGUI.

Run:
    python -m cimbar.gui

Requirements:
    pip install PySimpleGUI

This GUI provides a minimal interface to call the existing encode(...) and decode(...) functions
from cimbar.cimbar. It runs the encode/decode in a background thread so the UI remains responsive
and streams simple log messages to the UI.

Note: This GUI is intended for local use and quick testing. For packaging into a single-file
exe with PyInstaller, ensure PySimpleGUI is included in dependencies and test with --onedir first.
"""

import threading
import os
import traceback
from typing import List

import PySimpleGUI as sg

from cimbar.cimbar import encode, decode
from cimbar import conf


def _parse_images_field(value: str) -> List[str]:
    if not value:
        return []
    # PySimpleGUI returns multiple files as a single string separated by ; on Windows
    parts = [p for p in value.split(';') if p]
    return parts


def run_encode(window, src, dst_prefix, dark, ecc, fountain):
    try:
        window.write_event_value('-LOG-', f'Starting encode: src={src} dst_prefix={dst_prefix}')
        encode(src, dst_prefix, dark=dark, ecc=ecc, fountain=fountain)
        window.write_event_value('-LOG-', 'Encode finished successfully')
    except Exception as e:
        window.write_event_value('-LOG-', f'Encode error: {e}')
        window.write_event_value('-LOG-', traceback.format_exc())
    finally:
        window.write_event_value('-DONE-', True)


def run_decode(window, images: List[str], out_file, dark, ecc, fountain, force_preprocess=False, color_correct=0, deskew=True, auto_dewarp=False):
    try:
        window.write_event_value('-LOG-', f'Starting decode: images={images} out={out_file}')
        decode(images, out_file, dark=dark, ecc=ecc, fountain=fountain, force_preprocess=force_preprocess, color_correct=color_correct, deskew=deskew, auto_dewarp=auto_dewarp)
        window.write_event_value('-LOG-', 'Decode finished successfully')
    except Exception as e:
        window.write_event_value('-LOG-', f'Decode error: {e}')
        window.write_event_value('-LOG-', traceback.format_exc())
    finally:
        window.write_event_value('-DONE-', True)


def main():
    sg.theme('DefaultNoMoreNagging')

    mode_col = [
        [sg.Radio('Encode', 'MODE', key='-ENCODE-', default=True), sg.Radio('Decode', 'MODE', key='-DECODE-')]
    ]

    encode_col = [
        [sg.Text('Source file (to encode)'), sg.Input(key='-SRC-'), sg.FileBrowse(file_types=(('All files','*.*'),), key='-SRC-BROWSE-')],
        [sg.Text('Output image prefix'), sg.Input(key='-DST-'), sg.FileSaveAs(file_types=(('PNG','*.png'),), key='-DST-BROWSE-')],
    ]

    decode_col = [
        [sg.Text('Image files (multiple)'), sg.Input(key='-IMAGES-'), sg.FilesBrowse(file_types=(('PNG','*.png'),), key='-IMG-BROWSE-')],
        [sg.Text('Output binary file'), sg.Input(key='-OUT-'), sg.FileSaveAs(file_types=(('All files','*.*'),), key='-OUT-BROWSE-')],
    ]

    options_col = [
        [sg.Checkbox('Dark palette', key='-DARK-', default=False), sg.Checkbox('Fountain', key='-FOUNTAIN-', default=False)],
        [sg.Text('ECC (leave blank for default)'), sg.Input('', size=(10,1), key='-ECC-')],
    ]

    layout = [
        [sg.Frame('Mode', mode_col)],
        [sg.Frame('Encode', encode_col, visible=True, key='-FRAME-ENC-')],
        [sg.Frame('Decode', decode_col, visible=False, key='-FRAME-DEC-')],
        [sg.Frame('Options', options_col)],
        [sg.Button('Run', key='-RUN-'), sg.Button('Open output', key='-OPEN-', disabled=True), sg.Button('Exit')],
        [sg.Text('Log:')],
        [sg.Multiline('', size=(80,20), key='-LOG-', autoscroll=True, disabled=True)],
    ]

    window = sg.Window('cimbar GUI', layout)

    worker = None

    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        # toggle frames based on mode
        if event == '-ENCODE-' or event == '-DECODE-':
            enc = values['-ENCODE-']
            window['-FRAME-ENC-'].update(visible=enc)
            window['-FRAME-DEC-'].update(visible=not enc)

        if event == '-RUN-':
            if worker and worker.is_alive():
                sg.popup('Operation already running')
                continue

            dark = bool(values['-DARK-'])
            fountain = bool(values['-FOUNTAIN-'])
            ecc_val = values['-ECC-']
            try:
                ecc = int(ecc_val) if ecc_val.strip() else conf.ECC
            except Exception:
                sg.popup('ECC must be an integer if provided')
                continue

            if values['-ENCODE-']:
                src = values['-SRC-']
                dst = values['-DST-']
                if not src or not dst:
                    sg.popup('Please provide source file and output prefix for encode')
                    continue
                window['-OPEN-'].update(disabled=True)
                worker = threading.Thread(target=run_encode, args=(window, src, dst, dark, ecc, fountain), daemon=True)
                worker.start()
            else:
                imgs_field = values['-IMAGES-']
                images = _parse_images_field(imgs_field)
                out_file = values['-OUT-']
                if not images or not out_file:
                    sg.popup('Please provide image files and output filename for decode')
                    continue
                window['-OPEN-'].update(disabled=True)
                worker = threading.Thread(target=run_decode, args=(window, images, out_file, dark, ecc, fountain), daemon=True)
                worker.start()

        if event == '-LOG-':
            # not used; log events come via write_event_value below
            pass

        if event == '-DONE-':
            window['-OPEN-'].update(disabled=False)

        # custom log events arrive as strings with key '-LOG-'
        if event == '-LOG-':
            window['-LOG-'].print(values[event])

        # PySimpleGUI: events from write_event_value appear as a tuple (event, value) where value is in values[event]
        # We handle them by checking for presence of key in values and printing
        if '-LOG-' in values and values['-LOG-']:
            # values['-LOG-'] may be a single string or a list; print and then clear
            msg = values['-LOG-']
            window['-LOG-'].print(msg)
            # clear the value to avoid reprinting
            window['_last_log_'] = msg
            # work-around: can't directly clear values dict; rely on events instead

        # handle Open output
        if event == '-OPEN-':
            try:
                if values['-ENCODE-']:
                    out_path = values['-DST-']
                    # if encode produced multiple frames, user will need to open folder
                    if os.path.exists(out_path):
                        os.startfile(out_path)
                    else:
                        sg.popup(f'Output {out_path} not found')
                else:
                    out_path = values['-OUT-']
                    if os.path.exists(out_path):
                        os.startfile(out_path)
                    else:
                        sg.popup(f'Output {out_path} not found')
            except Exception as e:
                sg.popup(f'Open failed: {e}')

        # consume any events produced by worker via write_event_value
        if event == '-LOG-':
            pass

    window.close()


if __name__ == '__main__':
    main()
