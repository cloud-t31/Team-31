# Team-31

Development Steps:
1. source the CCC2017-Team31-openrc.sh file
2. Run Nova command: 
   nova boot test --min-count 3 --max-count 3  --flavor m1.medium --image 18bba5e4-d266-4209-9dde-2336465f0384 --key-name COMP90024 --security-groups default 
3. Check if the instances have been created
4. Run CreateHosts.py, check and configure 'hosts' file
5. Add comp90024.pem as private key
6. Run Ansible command:
   ansible-playbook -i host deployDB.yml
   ansible-playbook -i host web.yml
