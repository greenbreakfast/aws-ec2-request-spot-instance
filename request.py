import json
import subprocess
import time
from datetime import datetime

def systemCall(inputCmd):
    # create array from command
    inputCmdArray = inputCmd.split()
    # run the command
    out = subprocess.Popen(inputCmdArray,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

    # get stdout and std err
    stdout,stderr = out.communicate()

    return stdout

def systemCallJson(inputCmd):
    response = systemCall(inputCmd)
    try:
        ret = json.loads(response)
        pass
    except Exception as e:
        print('ERROR: executing command "%s"'%inputCmd)
        print(response)
        raise SystemExit(e)
    return ret

def printInstanceInfo(info):
    print(' ')
    print(' ')
    print(' ')

    print('*'*20)
    print('Spot instance launched and running')
    print('\tInstance ID:\t\t%s'%info['instanceId'])
    print('\tPublic IP Address:\t%s'%info['ipAddr'])
    print('\tSpot instance price:\t$%s / hr'%info['instancePrice'])
    print(' ')
    print('To shut down instance, run:')
    print('\taws ec2 cancel-spot-instance-requests --spot-instance-request-ids %s'%info['spotRequestId'])
    print('\taws ec2 terminate-instances --instance-ids %s'%info['instanceId'])
    print('*'*20)

def printInstanceInfoToFile(info, fileName):
    with open(fileName, "w") as f:
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

        f.write('Spot instance launched and running at %s\n'%dt_string)
        f.write('\tInstance ID:\t\t%s\n'%info['instanceId'])
        f.write('\tPublic IP Address:\t%s\n'%info['ipAddr'])
        f.write('\tSpot instance price:\t$%s / hr\n'%info['instancePrice'])
        f.write(' \n')
        f.write('To shut down instance, run:\n')
        f.write('\taws ec2 cancel-spot-instance-requests --spot-instance-request-ids %s\n'%info['spotRequestId'])
        f.write('\taws ec2 terminate-instances --instance-ids %s\n'%info['instanceId'])


def main():
    print(' Creating spot instance request ...')
    info = {}
    cmd = 'aws ec2 request-spot-instances --instance-count 1 --type one-time --launch-specification file://specification.json'
    ret = systemCallJson(cmd)
    info['spotRequestId'] = ret['SpotInstanceRequests'][0]['SpotInstanceRequestId']

    print(' Spot instance request created, id is %s'%info['spotRequestId'])


    print(' Waiting until spot instance is fulfilled ...')
    info['instanceId'] = ''
    info['instancePrice'] = ''
    count = 0

    while True:
        time.sleep(5)
        cmd = 'aws ec2 describe-spot-instance-requests --spot-instance-request-ids %s'%info['spotRequestId']
        ret = systemCallJson(cmd)
        # print(ret['SpotInstanceRequests'][0]['Status'])
        status = ret['SpotInstanceRequests'][0]['Status']['Code']

        if status == 'fulfilled':
            info['instanceId'] = ret['SpotInstanceRequests'][0]['InstanceId']
            info['instancePrice'] = ret['SpotInstanceRequests'][0]['SpotPrice']
            break
        print(' .', end = '')
        count += 1
        if count == 5:
            print('\n   - Spot Instance Request status: %s'%status)

    print(' Waiting for instance to initialize ...')
    info['ipAddr'] = ''
    count = 0

    while True:
        time.sleep(5)
        cmd = 'aws ec2 describe-instances --instance-ids %s'%info['instanceId']
        ret = systemCallJson(cmd)

        status = ret['Reservations'][0]['Instances'][0]['State']['Name']

        if status == 'running':
            info['ipAddr'] = ret['Reservations'][0]['Instances'][0]['PublicIpAddress']
            break
        print(' .', end = '')
        count += 1
        if count == 5:
            print('\n   - Instance status: %s'%status)

    printInstanceInfo(info)
    printInstanceInfoToFile(info, './instance.txt')

if __name__ == '__main__':
    main()
