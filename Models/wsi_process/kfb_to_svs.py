import os

num = 1
for i in range(0, num):
    # name = 'test_'
    # name = name + str(i)
    kfb_path = 'TCT\\NILM\\kfb\\'
    svs_path = 'TCT\\NILM\\svs\\'
    if not os.path.exists(svs_path):
        os.makedirs(svs_path)
    code_path = '\\KFBtoTIForSVS2.0\\x86'
    os.chdir(code_path)
    for kfb in os.listdir(kfb_path):
        kfb_file = os.path.join(kfb_path, kfb)
        svs_savepath = os.path.join(svs_path, svs_path)
        print(kfb_file)
        os.system('KFbioConverter.exe ' + str(kfb_file) + ' '
                  + str(os.path.join(svs_savepath, str(kfb.split('.')[0] + '.svs')) + ' 5'))
