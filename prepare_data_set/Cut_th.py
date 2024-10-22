import pandas
import docker
import os

def docker_cut( check_count, sent_path, data_path, save_path, container_name, mode ) :
    df = pandas.read_csv(f'{check_count}/count.csv') #ใช้ csv.reader() เพื่อสร้างอ็อบเจกต์ reader สำหรับอ่านข้อมูลจากไฟล์
    for i in range( 0, int( df.columns[ 0 ]) ) :
        if mode :
            status = send_curl( f'{data_path}/{i}.csv', f'{save_path}/thai_sentences_{i}.csv', container_name)
            if status :
                print( f'thai_sentences_{i}.csv' )
            else :
                print( f"Can't cut {i}.csv" )

        else :
            if not(os.path.exists( f'{sent_path}/thai_sentences_{i}.csv' ) ) :
                status = send_curl( f'{data_path}/{i}.csv', f'{save_path}/thai_sentences_{i}.csv', container_name)
                if status :
                    print( f'thai_sentences_{i}.csv' )
                else :
                    print( f"Can't cut {i}.csv" )

def send_curl( data_path, save_path, container_name ):
    client = docker.from_env()
    container = client.containers.get( container_name )
    exec_command = f'curl --location --request POST "localhost/cut_sent/" --form "data_path={data_path}" --form "save_path={save_path}"' #กำหนด command ที่จะรัน
    response = container.exec_run( exec_command ) #รัน command
    if response.exit_code == 0:
        return True
    else:
        return False

docker_cut( "./Prepare_data_set/data", "./Prepare_data_set/thai_sentences", "/app/data", "/app/thai_sentences", "tran_sent_cut", True )