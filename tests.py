import pandas
import os.path
from pathlib import Path
from core import models

def process_excel():
    path = f'{os.getcwd()}/booknails/static/files/'
    print(os.path.exists(path))
    filepath = f'{path}/Servicios.xlsx'
    print(os.path.isfile(filepath))
    excel = pandas.read_excel(filepath)

    for index, row in excel.iterrows():
        # print(f'{index}: {row.to_dict()}')
        servicio = models.Servicio(**row.to_dict())
        print(servicio)
        # for name, value in row.to_dict().items():
        #     print(f'{index}: {name}:{value}')




if __name__ == '__main__':
    process_excel()
