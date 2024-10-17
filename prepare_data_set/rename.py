import os

# ระบุเส้นทางไดเรกทอรีที่เก็บไฟล์
directory = './thai_sentences/'

# แสดงรายการไฟล์ทั้งหมดในไดเรกทอรีเพื่อการตรวจสอบ
print(f'Files in directory before renaming: {os.listdir(directory)}')

for i in range(0, 163):
    old_name = os.path.join(directory, f'{i}_thai_sentences.csv')
    new_name = os.path.join(directory, f'thai_sentences_{i}.csv')
    
    # แสดงชื่อไฟล์ที่กำลังตรวจสอบ
    print(f'Checking file: {old_name}')
    
    # ตรวจสอบว่าไฟล์ต้นทางมีอยู่จริงหรือไม่
    if os.path.exists(old_name):
        try:
            os.rename(old_name, new_name)
            print(f'Renamed: {old_name} to {new_name}')
            
            # ตรวจสอบว่าไฟล์ใหม่มีอยู่จริงหลังจากเปลี่ยนชื่อแล้ว
            if os.path.exists(new_name):
                print(f'File successfully renamed to: {new_name}')
            else:
                print(f'Error: File {new_name} does not exist after renaming.')
                
        except Exception as e:
            print(f'Error renaming {old_name} to {new_name}: {e}')
    else:
        print(f'File not found: {old_name}')
