from tkinter import Tk, filedialog

class FileOperator():
    '''
    File operations using filedialog or forward usage
    '''

    def load(self, filepath=None):
        if filepath:
            path = filepath
        else:
            root = Tk()
            root.withdraw()
            path = filedialog.askopenfilename(filetypes=(
                                                ('Pyno files', '*.pn'),
                                                ('All files', '*.*')))
            root.destroy()
        try:
            filepath = open(path, 'r')
        except Exception as ex:
            print('Can\'t load file:', ex)
            return None, path
        data = filepath.read()
        filepath.close()
        print('File', path, 'loaded!')
        return data, path

    def save(self, data, filepath=None, initialfile='pyno_file.pn'):
        if filepath:
            path = filepath
        else:
            root = Tk()
            root.withdraw()
            path = filedialog.asksaveasfilename(defaultextension='pn',
                                                initialfile=initialfile,
                                                filetypes=(
                                                    ('Pyno files', '*.pn'),
                                                    ('All files', '*.*')))
            root.destroy()
        try:
            file = open(path, 'w')
        except Exception as ex:
            print('Can\'t save file:', ex)
            return False
        file.write(data)
        file.close()
        print('File', path, 'saved!')
        return True