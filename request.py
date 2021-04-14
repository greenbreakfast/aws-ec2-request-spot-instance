import json
import subprocess
import time

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

def main():
    print(' Creating spot instance request ...')
    cmd = 'aws ec2 request-spot-instances --instance-count 1 --type one-time --launch-specification file://specification.json'
    ret = systemCallJson(cmd)
    spotRequestId = ret['SpotInstanceRequests'][0]['SpotInstanceRequestId']

    print(' Spot instance request created, id is %s'%spotRequestId)


    print(' Waiting until spot instance is fulfilled ...')
    instanceId = ''
    instancePrice = ''
    count = 0

    while True:
        time.sleep(5)
        cmd = 'aws ec2 describe-spot-instance-requests --spot-instance-request-ids %s'%spotRequestId
        ret = systemCallJson(cmd)
        # print(ret['SpotInstanceRequests'][0]['Status'])
        status = ret['SpotInstanceRequests'][0]['Status']['Code']

        if status == 'fulfilled':
            instanceId = ret['SpotInstanceRequests'][0]['InstanceId']
            instancePrice = ret['SpotInstanceRequests'][0]['SpotPrice']
            break
        print(' .', end = '')
        count += 1
        if count == 5:
            print('\n   - Spot Instance Request status: %s'%status)

    print(' Waiting for instance to initialize ...')
    ipAddr = ''
    count = 0

    while True:
        time.sleep(5)
        cmd = 'aws ec2 describe-instances --instance-ids %s'%instanceId
        ret = systemCallJson(cmd)

        status = ret['Reservations'][0]['Instances'][0]['State']['Name']

        if status == 'running':
            ipAddr = ret['Reservations'][0]['Instances'][0]['PublicIpAddress']
            break
        print(' .', end = '')
        count += 1
        if count == 5:
            print('\n   - Instance status: %s'%status)

    print(' ')
    print(' ')
    print(' ')

    print('*'*20)
    print('Spot instance launched and running')
    print('\tInstance ID:\t\t%s'%instanceId)
    print('\tPublic IP Address:\t%s'%ipAddr)
    print('\tSpot instance price:\t$%s / hr'%instancePrice)
    print(' ')
    print('To shut down instance, run:')
    print('\taws ec2 cancel-spot-instance-requests --spot-instance-request-ids %s'%spotRequestId)
    print('\taws ec2 terminate-instances --instance-ids %s'%instanceId)
    print('*'*20)

if __name__ == '__main__':
    main()
