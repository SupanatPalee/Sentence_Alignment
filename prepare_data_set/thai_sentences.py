import pandas
import subprocess
import docker
import time

def docker_ctrl( path, save_path, container_name ) :
    df = pandas.read_csv(f'{ path }count.csv') #ใช้ csv.reader() เพื่อสร้างอ็อบเจกต์ reader สำหรับอ่านข้อมูลจากไฟล์
    if( check_container_status( container_name ) ) :
        start_docker_container( container_name )
    for i in range( 0, int( df.columns[ 0 ]) ) :
        df = pandas.read_csv(f'{path}{i}.csv', usecols=[ 'Journal_link', 'Archives_link' ,'Archives_year' ,'Article_link', 'Thai_sentence' ])
        sentences = df.iloc[ 0 ,4 ]
        print( f"{i}) {sentences}" )
        print( "-----------------------------------------" )
        send_curl( f'{save_path}thai_sentences_{i}.csv', container_name, sentences )
    """if not( check_container_status( container_name ) ):
        stop_docker_container(container_name)"""

def check_container_status(container_name):
    try:
        result = subprocess.run(["docker", "ps", "-f", f"name={container_name}"], capture_output=True, text=True)
        if container_name in result.stdout:
            print(f"Container '{container_name}' is running.")
            return( False )
        else:
            print(f"Container '{container_name}' is not running.")
            return( True )
    except Exception as e:
        print(f"An error occurred: {e}")

def start_docker_container(container_name):
    try:
        # คำสั่ง Docker ที่ต้องการรัน
        command = ["docker", "start", container_name]
        # รันคำสั่ง
        result = subprocess.run(command, capture_output=True, text=True)
        # ตรวจสอบผลลัพธ์
        if result.returncode == 0:
            print(f"Container '{container_name}' started successfully.")
            print("Output:", result.stdout.strip())
            time.sleep( 10 )
        else:
            print(f"Failed to start container '{container_name}'.")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")

def send_curl( save_path, container_name, sentences ):
    client = docker.from_env()
    container = client.containers.get( container_name )
    #exec_command = f'curl --location --request POST "localhost/cut_sent/" --form "path={save_path}" --form "text={sentences}"'
    exec_command = f"curl --location --request POST 'localhost/cut_sent/' --form 'path={save_path}' --form 'text={sentences}'"
    
    
    container.exec_run( exec_command )

def stop_docker_container( container_name ):
    try:
        # สร้างคำสั่งในรูปแบบของการใช้งาน Docker CLI สำหรับหยุดคอนเทนเนอร์
        command = f"docker stop {container_name}"
        
        # ใช้ subprocess เพื่อรันคำสั่ง
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # ตรวจสอบผลลัพธ์
        if result.returncode == 0:
            print(f"Container {container_name} has been stopped successfully.")
        else:
            print("Failed to stop container.")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")

#docker_ctrl( "./data/", "/thai_sentences/", "some-name" )